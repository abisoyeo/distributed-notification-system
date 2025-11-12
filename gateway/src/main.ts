import * as dotenv from 'dotenv';
dotenv.config();
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { createDatabase } from 'typeorm-extension';
import { dataSourceOptions } from './db/data-source.options';

async function bootstrap() {
  await createDatabase({
    ifNotExist: true,
    options: dataSourceOptions,
  });

  const app = await NestFactory.create(AppModule);

  app.setGlobalPrefix('api');

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
