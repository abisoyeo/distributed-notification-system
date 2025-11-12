import { Inject, Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { NotificationStatus } from './entities/notification-status.entity';
import { UpdateStatusDto } from './dto/update-status.dto';
import { ClientProxy } from '@nestjs/microservices';
import { SendNotificationDto } from './dto/send-notification.dto';

@Injectable()
export class NotificationsService {
  constructor(
    @InjectRepository(NotificationStatus)
    private readonly statusRepo: Repository<NotificationStatus>,

    @Inject('NOTIFICATION_QUEUE') private client: ClientProxy,
  ) {}

  async publishToQueue(dto: SendNotificationDto) {
    return this.client.emit('send_notification', dto);
  }

  async updateStatus(dto: UpdateStatusDto) {
    const status = this.statusRepo.create(dto);
    return this.statusRepo.save(status);
  }

  async getStatuses(notificationId: string) {
    return this.statusRepo.find({ where: { notificationId } });
  }
}
