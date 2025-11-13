import { Injectable, Inject, HttpException, HttpStatus } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { SendNotificationDto } from './dto/send-notification.dto';
import { UpdateStatusDto } from './dto/update-status.dto';
import { NotificationRepository } from './notifications.repo.service';
import * as amqp from 'amqplib';

@Injectable()
export class NotificationsService {
  private readonly userServiceUrl =
    process.env.USER_SERVICE_URL || 'http://localhost:3001';
  private readonly templateServiceUrl =
    process.env.TEMPLATE_SERVICE_URL || 'http://localhost:3003';

  constructor(
    private readonly statusRepo: NotificationRepository,
    private readonly http: HttpService,
    @Inject('NOTIFICATION_EMAIL_QUEUE') private emailClient: ClientProxy,
    @Inject('NOTIFICATION_PUSH_QUEUE') private pushClient: ClientProxy,
  ) {}

  /**
   * Handles fetching data, routing logic, and queue publishing
   */
  async handleSendNotification(dto: SendNotificationDto) {
    try {
      // const userResponse = await firstValueFrom(
      //   this.http.get(`${this.userServiceUrl}/${dto.user_id}`),
      // );
      // const user = userResponse.data;

      // const templateResponse = await firstValueFrom(
      //   this.http.get(
      //     `${this.templateServiceUrl}/templates/${dto.template_code}`,
      //   ),
      // );
      // const template = templateResponse.data;

      // if (!user || !template) {
      //   throw new HttpException(
      //     'User or template not found',
      //     HttpStatus.NOT_FOUND,
      //   );
      // }

      // if (
      //   dto.notification_type === 'email' &&
      //   user.preferences?.email === false
      // ) {
      //   throw new HttpException(
      //     'User has disabled email notifications',
      //     HttpStatus.BAD_REQUEST,
      //   );
      // }
      // if (
      //   dto.notification_type === 'push' &&
      //   user.preferences?.push === false
      // ) {
      //   throw new HttpException(
      //     'User has disabled push notifications',
      //     HttpStatus.BAD_REQUEST,
      //   );
      // }

      // const content = this.mergeTemplate(template.content, dto.variables);

      // Mocked user & template data:
      const user = this.mockUserData(dto.user_id);
      const template = this.mockTemplateData(dto.template_code);

      const queuePayload = {
        pattern: 'email',
        data: {
          correlation_id: dto.request_id,
          to_email: user.email,
          template_id: template.id,
          language_code: template.language_code,
          data: {
            username: dto.variables.name || user.name,
            updateDate:
              dto.variables.meta?.date || new Date().toLocaleDateString(),
            settingsLink:
              dto.variables.link || 'https://your-service.com/settings',
          },
        },
      };

      const routingKey =
        dto.notification_type === 'email'
          ? 'email.queue'
          : dto.notification_type === 'push'
            ? 'push.queue'
            : null;

      if (!routingKey) {
        throw new HttpException(
          'Invalid notification type',
          HttpStatus.BAD_REQUEST,
        );
      }
      if (dto.notification_type === 'email') {
        // await firstValueFrom(this.emailClient.emit(routingKey, queuePayload));
        await this.publishToExchange(queuePayload);
      } else if (dto.notification_type === 'push') {
        // await firstValueFrom(this.pushClient.emit(routingKey, queuePayload));
      }

      await this.statusRepo.create({
        notificationId: dto.request_id,
        channel: dto.notification_type,
        status: 'pending',
        // messageId: dto.messageId,
        // errorMessage: dto.errorMessage,
        createdAt: new Date(),
      });

      return { success: true, routingKey };
    } catch (error) {
      if (error.response?.status === 404) {
        throw new HttpException(
          'User or template not found',
          HttpStatus.NOT_FOUND,
        );
      }
      throw new HttpException(
        error.message || 'Failed to process notification',
        error.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  async updateStatus(dto: UpdateStatusDto, notification_preference: string) {
    const id = dto.notificationId;
    return this.statusRepo.update(id, dto);
  }

  async getStatuses(notificationId: string) {
    return this.statusRepo.findOne(notificationId);
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

  async publishToExchange(payload: any) {
    const conn = await amqp.connect(
      process.env.RABBITMQ_URL || 'amqp://localhost:5672',
    );
    const channel = await conn.createChannel();

    const exchange = 'notifications.direct';
    const routingKey = 'email';

    await channel.publish(
      exchange,
      routingKey,
      Buffer.from(JSON.stringify(payload)),
      {
        persistent: true,
      },
    );

    await channel.close();
    await conn.close();
  }

  private mockUserData(userId: string) {
    const fakeUsers = [
      { id: '123', name: 'Abisoye', email: 'sands007821@gmail.com' },
      { id: '124', name: 'Immanuel', email: 'adekeyeimmanuel@gmail.com' },
      { id: '125', name: 'Olaitan', email: 'emmfatsneh@gmail.com' },
    ];

    const found = fakeUsers.find((u) => u.id === userId);
    return (
      found || {
        id: userId,
        name: `User_${userId}`,
        email: `${userId}@example.com`,
      }
    );
  }

  private mockTemplateData(templateCode: string) {
    const templates = {
      welcome_email: { id: 101, language_code: 'en' },
      pref_update: { id: 102, language_code: 'es' },
      password_reset: { id: 999, language_code: 'es' },
    };

    return templates[templateCode];
  }
}
