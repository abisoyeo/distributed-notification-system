import { ApiProperty } from '@nestjs/swagger';

export class NotificationResponse {
  @ApiProperty()
  success: boolean;
  @ApiProperty()
  message: string;
  @ApiProperty()
  notificationId?: string;
}
