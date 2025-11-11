import { Controller, Post, Body, Get, Param } from '@nestjs/common';
import { NotificationsService } from './notifications.service';
import { SendNotificationDto } from './dto/send-notification.dto';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { NotificationResponse } from './entities/notification.entity';

@Controller('notifications')
export class NotificationsController {
  private notificationServiceUrl =
    process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:3002';

  constructor(
    private readonly notificationsService: NotificationsService,
    private readonly http: HttpService,
  ) {}

  @Post('send-notification')
  async sendNotification(
    @Body() body: SendNotificationDto,
  ): Promise<NotificationResponse> {
    const response = await firstValueFrom(
      this.http.post<NotificationResponse>(
        `${this.notificationServiceUrl}/send`,
        body,
      ),
    );
    return response.data;
  }

  @Get('status/:id')
  status(@Param('id') id: string) {
    // Optional: can be implemented with Notification Service later
    return { id, status: 'queued' };
  }

  @Get('health')
  health() {
    return { status: 'ok' };
  }
}
