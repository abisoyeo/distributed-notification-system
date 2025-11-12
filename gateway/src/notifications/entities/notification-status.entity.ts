import { Schema } from 'redis-om';

export interface NotificationStatus {
  notificationId: string;
  channel: string;
  status: string;
  messageId?: string;
  errorMessage?: string;
  createdAt: Date;
}

export const notificationStatusSchema = new Schema('NotificationStatus', {
  notificationId: { type: 'string', indexed: true },
  channel: { type: 'string' },
  status: { type: 'string' },
  messageId: { type: 'string' },
  errorMessage: { type: 'string' },
  createdAt: { type: 'date', sortable: true },
});
