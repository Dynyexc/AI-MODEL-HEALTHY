import { Module } from '@nestjs/common';
import { AdminService } from './admin.service';
import { AdminController } from './admin.controller';
import { AuthModule } from '../auth/auth.module';
import { ConsultationModule } from '../consultation/consultation.module';

@Module({
  imports: [AuthModule, ConsultationModule],
  controllers: [AdminController],
  providers: [AdminService],
})
export class AdminModule {}