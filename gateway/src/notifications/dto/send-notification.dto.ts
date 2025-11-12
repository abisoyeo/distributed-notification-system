import {
  IsEnum,
  IsObject,
  IsOptional,
  IsString,
  IsUUID,
  IsInt,
  ValidateNested,
} from 'class-validator';
import { NotificationType } from '../enums/notification-type.enum';
import { UserDataDto } from './user-data.dto';
import { Type } from 'class-transformer';

export class SendNotificationDto {
  @IsEnum(NotificationType)
  notification_type: NotificationType;

  @IsUUID()
  user_id: string;

  @IsString()
  template_code: string;

  @ValidateNested()
  @Type(() => UserDataDto)
  variables: UserDataDto;

  @IsString()
  request_id: string;

  @IsInt()
  @IsOptional()
  priority?: number;

  @IsObject()
  @IsOptional()
  metadata?: Record<string, unknown>;
}

export class NotificationQueueDto extends SendNotificationDto {
  @IsString()
  recipient: string;

  @IsString()
  content: string;
}
