import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('notification_statuses')
export class NotificationStatus {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  notificationId: string; // corresponds to the notification the service is reporting on

  @Column()
  channel: string; // e.g. "email", "push", "sms"

  @Column()
  status: string; // e.g. "pending", "sent", "failed", "delivered"

  @Column({ nullable: true })
  messageId?: string; // optional — from email provider or push system

  @Column({ type: 'text', nullable: true })
  errorMessage?: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
