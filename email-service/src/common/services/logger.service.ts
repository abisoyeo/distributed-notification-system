import { Injectable, LoggerService as NestLogger, Scope } from '@nestjs/common';

@Injectable({ scope: Scope.TRANSIENT })
export class LoggerService implements NestLogger {
  private serviceName = 'email_service';
  private context: string = 'App';

  private logMessage(level: string, message: string, data: any) {
    console.log(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        level,
        service: this.serviceName,
        context: this.context,
        message,
        ...data,
      }),
    );
  }

  log(message: string, data?: any) {
    this.logMessage('INFO', message, data);
  }
  error(message: string, trace?: string, data?: any) {
    this.logMessage('ERROR', message, { trace, ...data });
  }
  warn(message: string, data?: any) {
    this.logMessage('WARN', message, data);
  }
  debug(message: string, data?: any) {
    this.logMessage('DEBUG', message, data);
  }

  setContext(context: string) {
    this.context = context;
  }
}
