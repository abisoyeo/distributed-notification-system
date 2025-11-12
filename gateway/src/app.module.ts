import { Module } from '@nestjs/common';
import { NotificationsModule } from './notifications/notifications.module';
import { UserModule } from './user/user.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { dataSourceOptions } from './db/data-source.options';

@Module({
  imports: [
    TypeOrmModule.forRoot(dataSourceOptions),
    NotificationsModule,
    UserModule,
  ],
})
export class AppModule {}
