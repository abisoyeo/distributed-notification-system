import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { RabbitMQSetupService } from './common/services/rabbitmq-setup.service';
import { ConfigService } from '@nestjs/config';

async function bootstrap() {
  const appContext = await NestFactory.createApplicationContext(AppModule);

  const setupService = appContext.get(RabbitMQSetupService);

  const configService = appContext.get(ConfigService);
  const rabbitConfig = configService.get('rabbit');

  await setupService.setupQueuesAndExchanges();

  const app = await NestFactory.create(AppModule);

  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.RMQ,
    options: {
      urls: [rabbitConfig.url],
      queue: rabbitConfig.emailQueue,
      queueOptions: {
        durable: true,
        deadLetterExchange: rabbitConfig.dlxExchange,
        deadLetterRoutingKey: 'retry.email.1',
        assertQueue: false,
      },
      noAck: false,
    },
  });

  await app.startAllMicroservices();

  await app.listen(3000, () => {
    console.log(
      `Application running and Microservice listener started on queue: ${rabbitConfig.emailQueue}`,
    );
  });
}
bootstrap();
