import { ApiProperty } from '@nestjs/swagger';
// import { IsAlphanumeric, MaxLength } from 'class-validator';

export class LoginDto {
  @ApiProperty()
  email: string;
  @ApiProperty()
  password: string;
}
