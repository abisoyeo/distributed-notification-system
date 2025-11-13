import { RabbitConfig } from '../common/interfaces';

export default () => ({
  templateServiceUrl:
    process.env.TEMPLATE_SERVICE_URL || 'http://template-service:8000',

  senderEmail: process.env.SENDER_EMAIL || 'skylar.gulgowski@ethereal.email',
  serviceName: process.env.SERVICE_NAME || 'email_service',

  smtp: {
    host: process.env.SMTP_HOST || 'smtp.ethereal.email',
    port: parseInt(process.env.SMTP_PORT ?? '587', 10) || 587,
    user: process.env.SMTP_USER || 'skylar.gulgowski@ethereal.email',
    pass: process.env.SMTP_PASS || 'z8W97rvk1szuZGWEvj',
  },

  rabbit: {
    url: process.env.RABBITMQ_URL || 'amqp://localhost:5672',
    emailQueue: process.env.EMAIL_QUEUE || 'email.queue',
    dlxExchange: process.env.DLX_EXCHANGE || 'dlx.exchange',
    failedQueue: process.env.FAILED_QUEUE || 'email.failed',
    maxRetries: parseInt(process.env.MAX_RETRIES ?? '3', 10),
    retryDelaysMs: [10000, 30000, 60000], // 10s, 30s, 60s
  } as RabbitConfig,
});
