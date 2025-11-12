import { Controller, Post, Body, Get, Param } from '@nestjs/common';
import { NotificationsService } from './notifications.service';
import {
  NotificationQueueDto,
  SendNotificationDto,
} from './dto/send-notification.dto';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { UpdateStatusDto } from './dto/update-status.dto';

@Controller('notifications')
export class NotificationsController {
  private userServiceUrl =
    process.env.USER_SERVICE_URL || 'http://localhost:3001';
  private templateServiceUrl =
    process.env.TEMPLATE_SERVICE_URL || 'http://localhost:3003';

  constructor(
    private readonly notificationsService: NotificationsService,
    private readonly http: HttpService,
  ) {}

  @Post('send-notification')
  async sendNotification(@Body() dto: SendNotificationDto) {
    const userResponse = await firstValueFrom(
      this.http.get(`${this.userServiceUrl}/users/${dto.user_id}`),
    );
    const user = userResponse.data;

    const templateResponse = await firstValueFrom(
      this.http.get(
        `${this.templateServiceUrl}/templates/${dto.template_code}`,
      ),
    );
    const template = templateResponse.data;

    const content = this.mergeTemplate(template.body, dto.variables);

    const queuePayload: NotificationQueueDto = {
      ...dto,
      recipient: user.email || user.push_token,
      content,
    };

    await this.notificationsService.publishToQueue(queuePayload);

    // 5️⃣ Optionally, persist notification record in your DB here

    return {
      request_id: dto.request_id,
      status: 'pending',
      type: dto.notification_type,
      user: dto.user_id,
    };
  }

  // This is the endpoint that other services (email, push, etc.) call
  @Post('status')
  async updateStatus(@Body() dto: UpdateStatusDto) {
    const result = await this.notificationsService.updateStatus(dto);
    return { success: true, result };
  }

  // Optional: for internal monitoring
  @Get(':notificationId/statuses')
  async getStatuses(@Param('notificationId') notificationId: string) {
    const statuses =
      await this.notificationsService.getStatuses(notificationId);
    return { success: true, statuses };
  }

  private mergeTemplate(
    template: string,
    variables: Record<string, any>,
  ): string {
    let result = template;
    for (const [key, value] of Object.entries(variables)) {
      result = result.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }
    return result;
  }
}
