import { Controller } from '@nestjs/common';
import {
  MessagePattern,
  Payload,
  RmqContext,
  Ctx,
} from '@nestjs/microservices';
import { EmailService } from './email.service';
import { EmailMessage, RabbitConfig } from '../common/interfaces';
import { ConfigService } from '@nestjs/config';
import { LoggerService } from '../common/services/logger.service';
import * as amqp from 'amqplib';

@Controller()
export class EmailController {
  private readonly rabbitConfig: RabbitConfig;
  private readonly logger: LoggerService;

  constructor(
    private readonly emailService: EmailService,
    private readonly configService: ConfigService,
  ) {
    const cfg = this.configService.get<RabbitConfig>('rabbit');
    if (!cfg) {
      throw new Error('RabbitMQ configuration is missing');
    }
    this.rabbitConfig = cfg;
    this.logger = new LoggerService();
  }

  @MessagePattern('email')
  async handleEmailMessage(
    @Payload() msg: EmailMessage,
    @Ctx() context: RmqContext,
  ): Promise<void> {
    const channel = context.getChannelRef() as amqp.Channel;
    const originalMessage = context.getMessage() as unknown as amqp.Message;

    const { correlation_id, retry_count = 0 } = msg;
    this.logger.log(`Received message (Attempt ${retry_count + 1}).`, {
      correlation_id,
    });

    try {
      await this.emailService.processEmailMessage(msg);
      channel.ack(originalMessage);
    } catch (error) {
      const err = error as Error;
      const nextRetryCount = retry_count + 1;

      this.logger.error(`Processing FAILED for message.`, err.message, {
        correlation_id,
        current_retry: retry_count,
      });

      if (nextRetryCount <= this.rabbitConfig.maxRetries) {
        const updatedContent = { ...msg, retry_count: nextRetryCount };
        const retryKey = `retry.email.${nextRetryCount}`;

        const envelopedMessage = {
          pattern: 'email',
          data: updatedContent,
        };

        channel.publish(
          this.rabbitConfig.dlxExchange,
          retryKey,
          Buffer.from(JSON.stringify(envelopedMessage)),
          { persistent: true },
        );

        channel.ack(originalMessage);

        this.logger.warn(`Message sent for retry ${nextRetryCount}.`, {
          correlation_id,
        });
      } else {
        channel.publish(
          this.rabbitConfig.dlxExchange,
          'failed.email',
          Buffer.from(JSON.stringify(msg)),
          { persistent: true },
        );
        channel.ack(originalMessage);
        this.logger.error(
          `Message permanently failed. Moved to ${this.rabbitConfig.failedQueue}.`,
        );
      }
    }
  }
}
