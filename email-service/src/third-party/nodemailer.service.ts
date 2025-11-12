import { Injectable } from '@nestjs/common';
import * as nodemailer from 'nodemailer';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class NodemailerService {
  private transporter: nodemailer.Transporter;
  private senderEmail: string;

  constructor(private configService: ConfigService) {
    const smtpConfig = this.configService.get('smtp');
    if (!smtpConfig) {
      throw new Error('SMTP configuration is missing');
    }
    const senderEmail = this.configService.get('senderEmail');
    if (!senderEmail) {
      throw new Error('Sender email is missing');
    }
    this.senderEmail = senderEmail;

    this.transporter = nodemailer.createTransport({
      host: smtpConfig.host,
      port: smtpConfig.port,
      secure: smtpConfig.port === 465,
      auth: {
        user: smtpConfig.user,
        pass: smtpConfig.pass,
      },
    });
  }

  async sendEmail(
    to: string,
    subject: string,
    html: string,
    correlationId: string,
  ): Promise<void> {
    const mailOptions = {
      from: this.senderEmail,
      to: to,
      subject: subject,
      html: html,
      headers: { 'X-Correlation-ID': correlationId },
    };

    await this.transporter.sendMail(mailOptions);
  }
}
