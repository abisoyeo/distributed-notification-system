export class SendNotificationDto {
  user_id: string;
  type: 'email' | 'push';
  template_id: string;
  variables: Record<string, any>;
}
