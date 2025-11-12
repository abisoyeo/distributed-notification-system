import * as dotenv from 'dotenv';
dotenv.config();
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { createDatabase } from 'typeorm-extension';
import { dataSourceOptions } from './db/data-source.options';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

async function bootstrap() {
  // await createDatabase({
  //   ifNotExist: true,
  //   options: dataSourceOptions,
  // });

  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('Notification API')
    .setDescription('API for updating notification statuses')
    .setVersion('1.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  app.setGlobalPrefix('api');

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
