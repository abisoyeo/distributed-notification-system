import { IsObject, IsOptional, IsString, IsUrl } from 'class-validator';

export class UserDataDto {
  @IsString()
  name: string;

  @IsUrl()
  link: string;

  @IsObject()
  @IsOptional()
  meta?: Record<string, unknown>;
}
