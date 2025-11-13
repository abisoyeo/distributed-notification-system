import { IsString, IsNotEmpty, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class UpdateStatusDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  notificationId: string;

  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  channel: string;

  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  status: string;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  messageId?: string;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  errorMessage?: string;
}
