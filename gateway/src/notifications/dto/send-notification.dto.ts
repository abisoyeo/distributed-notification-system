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
import { ApiProperty } from '@nestjs/swagger';

export class SendNotificationDto {
  @ApiProperty({ enum: NotificationType })
  @IsEnum(NotificationType)
  notification_type: NotificationType;

  @ApiProperty()
  @IsUUID()
  user_id: string;

  @ApiProperty()
  @IsString()
  template_code: string;

  @ApiProperty()
  @ValidateNested()
  @Type(() => UserDataDto)
  variables: UserDataDto;

  @ApiProperty()
  @IsString()
  request_id: string;

  @ApiProperty({ required: false })
  @IsInt()
  @IsOptional()
  priority?: number;

  @ApiProperty({ required: false })
  @IsObject()
  @IsOptional()
  metadata?: Record<string, unknown>;
}

export class NotificationQueueDto extends SendNotificationDto {
  @ApiProperty()
  @IsString()
  recipient: string;

  @ApiProperty()
  @IsString()
  content: string;
}
