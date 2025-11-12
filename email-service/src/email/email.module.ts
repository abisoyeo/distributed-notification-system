import { Module } from '@nestjs/common';
import { EmailService } from './email.service';
import { EmailController } from './email.controller';
import { NodemailerService } from '../third-party/nodemailer.service';
import { LoggerService } from '../common/services/logger.service';
import { CircuitBreakerService } from '../third-party/circuit-breaker.service';
import { RabbitMQSetupService } from '../common/services/rabbitmq-setup.service';
import { HttpModule } from '@nestjs/axios';

@Module({
  imports: [HttpModule],
  controllers: [EmailController],
  providers: [
    EmailService,
    NodemailerService,
    LoggerService,
    CircuitBreakerService,
    RabbitMQSetupService,
  ],
})
export class EmailModule {}
