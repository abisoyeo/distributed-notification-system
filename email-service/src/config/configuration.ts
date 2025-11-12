import { RabbitConfig } from '../common/interfaces';

export default () => ({
  templateServiceUrl:
    process.env.TEMPLATE_SERVICE_URL || 'http://template_service:8080',
  senderEmail: process.env.SENDER_EMAIL || 'notification@nest.com',
  serviceName: 'email_service',

  // Example SMTP settings (for Nodemailer)
  smtp: {
    host: process.env.SMTP_HOST || 'smtp.ethereal.email',
    port: parseInt(process.env.SMTP_PORT ?? '587', 10) || 587,
    user: process.env.SMTP_USER || 'placeholder',
    pass: process.env.SMTP_PASS || 'placeholder',
  },

  // RabbitMQ Configuration
  rabbit: {
    url: process.env.RABBITMQ_URL || 'amqp://user:password@rabbitmq',
    emailQueue: 'email.queue',
    dlxExchange: 'dlx.exchange',
    failedQueue: 'email.failed',
    maxRetries: 3,
    retryDelaysMs: [10000, 30000, 60000], // 10s, 30s, 60s
  } as RabbitConfig,
});
