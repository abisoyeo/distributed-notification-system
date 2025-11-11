import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { lastValueFrom } from 'rxjs';
import { SendNotificationDto } from './dto/send-notification.dto';
import { NOTIFICATION_SERVICE_URL } from '../config/services.config';

@Injectable()
export class NotificationsService {
  constructor(private readonly httpService: HttpService) {}

  async forwardToNotificationService(dto: SendNotificationDto) {
    // Forward request to Notification Service
    try {
      const response = await lastValueFrom(
        this.httpService.post(
          `${NOTIFICATION_SERVICE_URL}/send-notification`,
          dto,
        ),
      );
      return response.data;
    } catch (err) {
      console.error('Error forwarding to Notification Service:', err.message);
      return { status: 'error', message: err.message };
    }
  }
}
