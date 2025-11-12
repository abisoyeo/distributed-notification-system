import { Module } from '@nestjs/common';
import { NotificationsModule } from './notifications/notifications.module';
import { UserModule } from './user/user.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { dataSourceOptions } from './db/data-source.options';
import { RedisModule } from './redis/redis.module';

@Module({
  imports: [
    RedisModule,
    // TypeOrmModule.forRoot({ ...dataSourceOptions, autoLoadEntities: true }),
    NotificationsModule,
    UserModule,
  ],
})
export class AppModule {}
