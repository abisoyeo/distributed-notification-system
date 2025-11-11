import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { NotificationsModule } from './notifications/notifications.module';
import { UserModule } from './user/user.module';

@Module({
  imports: [NotificationsModule, UserModule, HttpModule],
})
export class AppModule {}
