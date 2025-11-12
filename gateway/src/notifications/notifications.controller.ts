import {
  Controller,
  Post,
  Body,
  Get,
  Param,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { NotificationsService } from './notifications.service';
import { SendNotificationDto } from './dto/send-notification.dto';
import { UpdateStatusDto } from './dto/update-status.dto';

@Controller('notifications')
export class NotificationsController {
  constructor(private readonly notificationsService: NotificationsService) {}

  /**
   * Gateway endpoint that accepts notification requests
   */
  @Post('send-notification')
  async sendNotification(@Body() dto: SendNotificationDto) {
    try {
      const result =
        await this.notificationsService.handleSendNotification(dto);
      return {
        request_id: dto.request_id,
        status: 'pending',
        type: dto.notification_type,
        user: dto.user_id,
        result,
      };
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to send notification',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Endpoint for worker services (email/push) to update statuses
   */
  @Post(':notification_preference/status')
  async updateStatus(
    @Param('notificationId') notification_preference: string,
    @Body() dto: UpdateStatusDto,
  ) {
    const result = await this.notificationsService.updateStatus(
      dto,
      notification_preference,
    );
    return { success: true, result };
  }

  /**
   * Optional internal monitoring endpoint
   */
  @Get(':notificationId/statuses')
  async getStatuses(@Param('notificationId') notificationId: string) {
    const statuses =
      await this.notificationsService.getStatuses(notificationId);
    return { success: true, statuses };
  }
}
