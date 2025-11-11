import { UserService } from './user.service';
import { Controller, Post, Body } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { SignupDto } from './dto/signup.dto';
import { LoginDto } from './dto/login.dto';
import { UserResponse } from './entities/user.entity';

@Controller('user')
export class UserController {
  private userServiceUrl =
    process.env.USER_SERVICE_URL || 'http://localhost:3001';

  constructor(
    private http: HttpService,
    private readonly userService: UserService,
  ) {}

  @Post('signup')
  async signup(@Body() body: SignupDto): Promise<UserResponse> {
    const response = await firstValueFrom(
      this.http.post<UserResponse>(`${this.userServiceUrl}/signup`, body),
    );
    return response.data;
  }

  @Post('login')
  async login(@Body() body: LoginDto): Promise<UserResponse> {
    const response = await firstValueFrom(
      this.http.post<UserResponse>(`${this.userServiceUrl}/login`, body),
    );
    return response.data;
  }
}
