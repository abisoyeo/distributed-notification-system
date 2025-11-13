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
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBody,
  ApiParam,
} from '@nestjs/swagger';

@ApiTags('notifications')
@Controller('notifications')
export class NotificationsController {
  constructor(private readonly notificationsService: NotificationsService) {}

  /**
   * Gateway endpoint that accepts notification requests
   */
  @Post('send-notification')
  @ApiOperation({ summary: 'Send a notification' })
  @ApiBody({ type: SendNotificationDto })
  @ApiResponse({
    status: 201,
    description: 'The notification has been successfully queued.',
  })
  @ApiResponse({ status: 400, description: 'Bad Request.' })
  @ApiResponse({ status: 500, description: 'Internal Server Error.' })
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
  @ApiOperation({ summary: 'Update notification status' })
  @ApiParam({
    name: 'notification_preference',
    description: 'The notification preference (e.g., email, push)',
  })
  @ApiBody({ type: UpdateStatusDto })
  @ApiResponse({
    status: 201,
    description: 'The status has been successfully updated.',
  })
  @ApiResponse({ status: 400, description: 'Bad Request.' })
  @ApiResponse({ status: 500, description: 'Internal Server Error.' })
  async updateStatus(
    @Param('notification_preference') notification_preference: string,
    @Body() dto: UpdateStatusDto,
  ) {
    try {
      const result = await this.notificationsService.updateStatus(
        dto,
        notification_preference,
      );
      return { success: true, result };
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to update status',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  /**
   * Optional internal monitoring endpoint
   */
  @Get(':notificationId/statuses')
  @ApiOperation({ summary: 'Get notification statuses' })
  @ApiParam({
    name: 'notificationId',
    description: 'The ID of the notification',
  })
  @ApiResponse({
    status: 200,
    description: 'The notification statuses.',
  })
  @ApiResponse({ status: 500, description: 'Internal Server Error.' })
  async getStatuses(@Param('notificationId') notificationId: string) {
    try {
      const statuses =
        await this.notificationsService.getStatuses(notificationId);
      return { success: true, statuses };
    } catch (error) {
      throw new HttpException(
        error.message || 'Failed to retrieve statuses',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
