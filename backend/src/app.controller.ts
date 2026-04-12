import { Controller, Get } from '@nestjs/common';
import { InjectConnection } from '@nestjs/mongoose';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { Connection } from 'mongoose';

@ApiTags('Health')
@Controller('health')
export class AppController {
  constructor(@InjectConnection() private connection: Connection) {}

  @Get()
  @ApiOperation({ summary: 'Kiểm tra trạng thái server và database' })
  check() {
    const dbState = ['disconnected', 'connected', 'connecting', 'disconnecting'];
    return {
      status: 'OK',
      timestamp: new Date().toISOString(),
      database: dbState[this.connection.readyState] ?? 'unknown',
    };
  }
}