import { Module } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { NotificationsController } from './notifications.controller';
import { TypeOrmModule } from '@nestjs/typeorm';

import { NotificationsService } from './notifications.service';
import { HttpModule } from '@nestjs/axios';
import { NotificationStatus } from './entities/notification-status.entity';

@Module({
  imports: [
    HttpModule,
    TypeOrmModule.forFeature([NotificationStatus]),
    ClientsModule.register([
      {
        name: 'NOTIFICATION_QUEUE',
        transport: Transport.RMQ,
        options: {
          urls: [process.env.RABBITMQ_URL || 'amqp://localhost:5672'],
          queue: 'notifications_queue',
          queueOptions: { durable: true },
        },
      },
    ]),
  ],
  controllers: [NotificationsController],
  providers: [NotificationsService],
})
export class NotificationsModule {}
