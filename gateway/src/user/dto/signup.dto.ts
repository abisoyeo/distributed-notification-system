import { ApiProperty } from '@nestjs/swagger';
// import { IsAlphanumeric, MaxLength } from 'class-validator';

export class SignupDto {
  @ApiProperty()
  email: string;
  password: string;
  preferences?: {
    email?: boolean;
    push?: boolean;
    sms?: boolean;
  };
}
