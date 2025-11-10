import { Controller, Post, Body, Get, Param } from '@nestjs/common';
import { NotificationsService } from './notifications.service';
import { SendNotificationDto } from './dto/send-notification.dto';

@Controller('notifications')
export class NotificationsController {
  constructor(private readonly notificationsService: NotificationsService) {}

  @Post('send-notification')
  async sendNotification(@Body() dto: SendNotificationDto) {
    return this.notificationsService.forwardToNotificationService(dto);
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
