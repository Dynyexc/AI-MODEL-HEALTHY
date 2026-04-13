import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { Consultation, ConsultationSchema } from './consultation.schema';
import { HealthProfile, HealthProfileSchema } from '../profile/health-profile.schema';
import { User, UserSchema } from '../auth/user.schema';
import { ConsultationService } from './consultation.service';
import { ConsultationController } from './consultation.controller';
import { AiService } from './ai.service';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: Consultation.name, schema: ConsultationSchema },
      { name: HealthProfile.name, schema: HealthProfileSchema },
      { name: User.name, schema: UserSchema },
    ]),
  ],
  controllers: [ConsultationController],
  providers: [ConsultationService, AiService],
  exports: [MongooseModule],
})
export class ConsultationModule {}