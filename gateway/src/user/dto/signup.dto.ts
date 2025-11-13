import { ApiProperty } from '@nestjs/swagger';
// import { IsAlphanumeric, MaxLength } from 'class-validator';

export class SignupDto {
  @ApiProperty()
  email: string;
  @ApiProperty()
  password: string;

  @ApiProperty({
    required: false,
    example: { email: true, push: false, sms: true },
  })
  preferences?: {
    email?: boolean;
    push?: boolean;
    sms?: boolean;
  };
}
