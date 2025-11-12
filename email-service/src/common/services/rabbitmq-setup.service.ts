// src/common/services/rabbitmq-setup.service.ts

import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as amqp from 'amqplib';
import { RabbitConfig } from '../interfaces';

@Injectable()
export class RabbitMQSetupService {
  private readonly logger = new Logger(RabbitMQSetupService.name);
  private readonly rabbitConfig: RabbitConfig;

  constructor(private readonly configService: ConfigService) {
    const cfg = this.configService.get<RabbitConfig>('rabbit');
    if (!cfg) {
      throw new Error('RabbitMQ configuration is missing');
    }
    this.rabbitConfig = cfg;
  }

  async setupQueuesAndExchanges(): Promise<void> {
    const {
      url,
      emailQueue,
      dlxExchange,
      failedQueue,
      maxRetries,
      retryDelaysMs,
    } = this.rabbitConfig;

    try {
      const connection = await amqp.connect(url);
      const channel = await connection.createChannel();

      this.logger.log('Successfully connected to RabbitMQ for setup.');

      await channel.assertExchange('notifications.direct', 'direct', {
        durable: true,
      });

      await channel.assertExchange(dlxExchange, 'topic', { durable: true });

      await channel.assertQueue(failedQueue, { durable: true });
      await channel.bindQueue(failedQueue, dlxExchange, 'failed.email');

      for (let i = 0; i < maxRetries; i++) {
        const delay = retryDelaysMs[i];
        const retryQueue = `${emailQueue}.retry.${i + 1}`;
        const retryRoutingKey = `retry.email.${i + 1}`;

        await channel.assertQueue(retryQueue, {
          durable: true,
          messageTtl: delay,
          deadLetterExchange: 'notifications.direct',
          deadLetterRoutingKey: 'email',
        });
        await channel.bindQueue(retryQueue, dlxExchange, retryRoutingKey);
      }

      await channel.assertQueue(emailQueue, {
        durable: true,
        deadLetterExchange: dlxExchange,
        deadLetterRoutingKey: 'retry.email.1',
      });
      await channel.bindQueue(emailQueue, 'notifications.direct', 'email');

      await channel.close();
      await connection.close();
      this.logger.log(
        `RabbitMQ setup for '${emailQueue}' completed successfully.`,
      );
    } catch (error) {
      this.logger.error(
        'Failed to set up RabbitMQ infrastructure.',
        error.message,
      );
      throw error;
    }
  }
}
