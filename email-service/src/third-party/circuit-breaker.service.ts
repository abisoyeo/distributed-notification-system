import { HttpService } from '@nestjs/axios';
import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class CircuitBreakerService {
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private failureCount = 0;
  private lastFailureTime = 0;
  private readonly failureThreshold = 5;
  private readonly resetTimeout = 30000;

  constructor(private readonly httpService: HttpService) {}

  async execute<T>(url: string): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime < this.resetTimeout) {
        throw new HttpException(
          'Circuit Breaker: OPEN. Service unavailable.',
          HttpStatus.SERVICE_UNAVAILABLE,
        );
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const response = await firstValueFrom(this.httpService.get(url));

      if (this.state !== 'CLOSED') {
        this.success();
      }

      if (response.status >= 400) {
        throw new HttpException(
          `External service returned ${response.status}`,
          response.status,
        );
      }
      return response.data;
    } catch (e) {
      this.fail();
      throw new Error(
        `CircuitBreaker: Request failed. State: ${this.state}. Error: ${e.message}`,
      );
    }
  }

  private fail() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    if (
      this.state === 'HALF_OPEN' ||
      this.failureCount >= this.failureThreshold
    ) {
      this.state = 'OPEN';
    }
  }

  private success() {
    this.state = 'CLOSED';
    this.failureCount = 0;
  }
}
