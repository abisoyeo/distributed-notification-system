import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { NotificationsController } from './notifications.controller';
import { NotificationsService } from './notifications.service';
import { HttpModule } from '@nestjs/axios';
import { NotificationRepository } from './notifications.repo.service';

@Module({
  imports: [
    HttpModule,
    ClientsModule.register([
      {
        name: 'NOTIFICATION_EMAIL_QUEUE',
        transport: Transport.RMQ,
        options: {
          urls: [process.env.RABBITMQ_URL || 'amqp://localhost:5672'],
          queue: 'email.queue', // Queue dedicated for emails
          queueOptions: { durable: true },
        },
      },
      {
        name: 'NOTIFICATION_PUSH_QUEUE',
        transport: Transport.RMQ,
        options: {
          urls: [process.env.RABBITMQ_URL || 'amqp://localhost:5672'],
          queue: 'push.queue', // Queue dedicated for push
          queueOptions: {
            durable: true,
            arguments: {
              'x-dead-letter-exchange': 'dlx.notifications',
              'x-dead-letter-routing-key': 'retry.email.1',
            },
          },
        },
      },
    ]),
  ],
  controllers: [NotificationsController],
  providers: [NotificationsService, NotificationRepository],
})
export class NotificationsModule {}
