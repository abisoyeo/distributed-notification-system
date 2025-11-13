import { Injectable } from '@nestjs/common';
import { NodemailerService } from '../third-party/nodemailer.service';
import { CircuitBreakerService } from '../third-party/circuit-breaker.service';
import { LoggerService } from '../common/services/logger.service';
import { EmailMessage } from '../common/interfaces';
import { ConfigService } from '@nestjs/config';
import * as Handlebars from 'handlebars';
import { HttpService } from '@nestjs/axios';
import { DEFAULT_TEMPLATES } from './utils/default-templates';

@Injectable()
export class EmailService {
  private readonly templateServiceUrl: string;

  constructor(
    private readonly nodemailerService: NodemailerService,
    private readonly configService: ConfigService,
    private readonly httpService: HttpService,
    private readonly logger: LoggerService,
  ) {
    this.logger.setContext(EmailService.name);
    const templateServiceUrl = this.configService.get('templateServiceUrl');
    if (!templateServiceUrl) {
      throw new Error('Template Service URL is missing');
    }
    this.templateServiceUrl = templateServiceUrl;
  }
  async fetchTemplate(
    templateId: number,
    languageCode: string,
    data: Record<string, any>, // ⭐ FIX: Data parameter added here for fallback rendering
    correlationId: string,
  ): Promise<any> {
    const breaker = new CircuitBreakerService(this.httpService);

    const url = `${this.templateServiceUrl}/templates/${templateId}/${languageCode}`;

    this.logger.log(
      `Fetching template ID ${templateId} for language ${languageCode}`,
      { correlationId, url },
    );

    try {
      const response: any = await breaker.execute(url);

      if (response && response.data) {
        // Successful external fetch
        return response.data;
      }

      throw new Error('Malformed response from template service');
    } catch (error: any) {
      // ⚠️ FALLBACK LOGIC
      this.logger.warn(
        `Template service FAILED. Falling back to local template for ID ${templateId}.`,
        { correlationId, error: error.message },
      );

      const defaultTemplate = DEFAULT_TEMPLATES[templateId];

      if (defaultTemplate) {
        // ⭐ FIX: Render content using the provided 'data' object
        const renderedContent = defaultTemplate.content(data);

        return {
          subject: defaultTemplate.subject,
          email_content: renderedContent, // Fully rendered HTML string
          body_html: renderedContent, // Critical for compilation check bypass
          is_fallback_prerendered: true, // ⭐ CRITICAL FLAG for renderTemplate bypass
        };
      }

      this.logger.error(
        `FATAL: No local fallback found for ID ${templateId}. Triggering retry.`,
      );
      throw new Error(`Template not available: ID ${templateId}`);
    }
  }

  renderTemplate(
    templateData: any,
    data: Record<string, any>,
  ): { subject: string; body: string } {
    const subjectTemplate = Handlebars.compile(templateData.subject);
    const finalSubject = subjectTemplate(data);

    if (templateData.is_fallback_prerendered) {
      this.logger.warn(
        'Using pre-rendered fallback content. Bypassing layout compilation.',
      );
      return { subject: finalSubject, body: templateData.body_html };
    }

    const contentTemplate = Handlebars.compile(templateData.email_content);
    const renderedContent = contentTemplate(data);

    const layoutTemplate = Handlebars.compile(templateData.body_html);
    const finalBody = layoutTemplate({
      ...data,
      content_body: renderedContent,
    });

    this.logger.debug('Handlebars rendering complete.', {
      templateId: templateData.id,
    });
    return { subject: finalSubject, body: finalBody };
  }

  async processEmailMessage(message: EmailMessage): Promise<void> {
    const {
      correlation_id,
      to_email,
      template_id,
      data,
      language_code = 'en',
    } = message;

    const templateData = await this.fetchTemplate(
      template_id,
      language_code,
      data,
      correlation_id,
    );

    const { subject, body } = this.renderTemplate(templateData, data);

    await this.nodemailerService.sendEmail(
      to_email,
      subject,
      body,
      correlation_id,
    );

    this.logger.log('Email successfully processed and sent.', {
      correlation_id,
      to_email,
    });
  }
}
