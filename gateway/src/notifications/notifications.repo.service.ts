import { Inject, Injectable } from '@nestjs/common';
import Redis from 'ioredis';
import { NotificationStatus } from './entities/notification-status.entity';

@Injectable()
export class NotificationRepository {
  private readonly prefix = 'notification:';

  constructor(@Inject('REDIS_CLIENT') private readonly redis: Redis) {}

  async create(status: NotificationStatus): Promise<void> {
    const key = this.prefix + status.notificationId;
    await this.redis.set(key, JSON.stringify(status));
  }

  async findOne(id: string): Promise<NotificationStatus | null> {
    const key = this.prefix + id;
    const data = await this.redis.get(key);
    if (!data) return null;
    return JSON.parse(data);
  }

  async update(
    id: string,
    updateData: Partial<NotificationStatus>,
  ): Promise<NotificationStatus | null> {
    const existing = await this.findOne(id);
    if (!existing) return null;
    const updated = { ...existing, ...updateData };
    await this.redis.set(this.prefix + id, JSON.stringify(updated));
    return updated;
  }
}
