import { ApiProperty } from '@nestjs/swagger';
import { IsObject, IsOptional, IsString, IsUrl } from 'class-validator';

export class UserDataDto {
  @ApiProperty()
  @IsString()
  name: string;

  @ApiProperty()
  @IsUrl()
  link: string;

  @ApiProperty({ required: false })
  @IsObject()
  @IsOptional()
  meta?: Record<string, unknown>;
}
