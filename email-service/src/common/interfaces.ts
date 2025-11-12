export interface EmailMessage {
  correlation_id: string;
  to_email: string;
  template_id: number;
  data: Record<string, any>;
  retry_count?: number;
}

export interface RabbitConfig {
  url: string;
  emailQueue: string;
  dlxExchange: string;
  maxRetries: number;
  retryDelaysMs: number[];
  failedQueue: string;
}
