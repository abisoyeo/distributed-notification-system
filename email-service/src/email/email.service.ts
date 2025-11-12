import { Injectable } from '@nestjs/common';
import { NodemailerService } from '../third-party/nodemailer.service';
import { CircuitBreakerService } from '../third-party/circuit-breaker.service';
import { LoggerService } from '../common/services/logger.service';
import { EmailMessage } from '../common/interfaces';
import { ConfigService } from '@nestjs/config';
import * as Handlebars from 'handlebars';
import { HttpService } from '@nestjs/axios';

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

  async fetchTemplate(templateId: number, correlationId: string): Promise<any> {
    const breaker = new CircuitBreakerService(this.httpService);
    const url = `${this.templateServiceUrl}/templates/${templateId}?language_code=en`;
    this.logger.log(`Fetching template ID ${templateId}`, { correlationId });
    const response = (await breaker.execute(url)) as { data: any } | unknown;
    if (response && typeof response === 'object' && 'data' in response) {
      return (response as any).data;
    }
    throw new Error('Invalid response from template service');
  }

  renderTemplate(
    templateData: any,
    data: Record<string, any>,
  ): { subject: string; body: string } {
    const contentTemplate = Handlebars.compile(templateData.email_content);
    const renderedContent = contentTemplate(data);

    const layoutTemplate = Handlebars.compile(templateData.body_html);
    const finalBody = layoutTemplate({
      ...data,
      content_body: renderedContent,
    });

    const subjectTemplate = Handlebars.compile(templateData.subject);
    const finalSubject = subjectTemplate(data);

    this.logger.debug('Handlebars rendering complete.', {
      templateId: templateData.id,
    });
    return { subject: finalSubject, body: finalBody };
  }

  async processEmailMessage(message: EmailMessage): Promise<void> {
    const { correlation_id, to_email, template_id, data } = message;

    const templateData = await this.fetchTemplate(template_id, correlation_id);
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
