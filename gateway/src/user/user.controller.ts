import { UserService } from './user.service';
import {
  Controller,
  Post,
  Body,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { SignupDto } from './dto/signup.dto';
import { LoginDto } from './dto/login.dto';
import { UserResponse } from './entities/user.entity';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBody,
} from '@nestjs/swagger';

@ApiTags('user')
@Controller('user')
export class UserController {
  private userServiceUrl =
    process.env.USER_SERVICE_URL || 'http://localhost:3001';

  constructor(
    private http: HttpService,
    private readonly userService: UserService,
  ) {}

  @Post('signup')
  @ApiOperation({ summary: 'User Signup' })
  @ApiResponse({
    status: 201,
    description: 'The user has been successfully created.',
    type: UserResponse,
  })
  @ApiResponse({ status: 400, description: 'Bad Request.' })
  @ApiResponse({ status: 500, description: 'Internal Server Error.' })
  async signup(@Body() body: SignupDto): Promise<UserResponse> {
    try {
      const response = await firstValueFrom(
        this.http.post<UserResponse>(`${this.userServiceUrl}/signup`, body),
      );
      return response.data;
    } catch (error) {
      throw new HttpException(
        error.response?.data?.message || 'Failed to sign up',
        error.response?.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Post('login')
  @ApiOperation({ summary: 'User Login' })
  @ApiResponse({
    status: 200,
    description: 'User logged in successfully.',
    type: UserResponse,
  })
  @ApiResponse({ status: 401, description: 'Unauthorized.' })
  @ApiResponse({ status: 500, description: 'Internal Server Error.' })
  async login(@Body() body: LoginDto): Promise<UserResponse> {
    try {
      const response = await firstValueFrom(
        this.http.post<UserResponse>(`${this.userServiceUrl}/login`, body),
      );
      return response.data;
    } catch (error) {
      throw new HttpException(
        error.response?.data?.message || 'Failed to log in',
        error.response?.status || HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
