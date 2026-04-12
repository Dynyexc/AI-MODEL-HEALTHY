import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as nodemailer from 'nodemailer';

@Injectable()
export class MailService {
  private transporter: nodemailer.Transporter;

  constructor(private config: ConfigService) {
    this.transporter = nodemailer.createTransport({
      host:   this.config.get('MAIL_HOST', 'smtp.gmail.com'),
      port:   this.config.get<number>('MAIL_PORT', 587),
      secure: false,
      auth: {
        user: this.config.get('MAIL_USER'),
        pass: this.config.get('MAIL_PASS'),
      },
    });
  }

  async sendOtp(to: string, otp: string) {
    try {
      await this.transporter.sendMail({
        from:    this.config.get('MAIL_FROM', 'HealthLine <no-reply@healthline.com>'),
        to,
        subject: '[HealthLine] Mã xác nhận đặt lại mật khẩu',
        html: `
          <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px">
            <h2 style="color:#16a34a">🏥 HealthLine</h2>
            <p>Bạn vừa yêu cầu đặt lại mật khẩu.</p>
            <p>Mã OTP của bạn là:</p>
            <div style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#16a34a;text-align:center;padding:16px 0">
              ${otp}
            </div>
            <p style="color:#6b7280;font-size:14px">Mã có hiệu lực trong <strong>10 phút</strong>. Không chia sẻ mã này cho ai.</p>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0"/>
            <p style="color:#9ca3af;font-size:12px">Nếu bạn không yêu cầu, hãy bỏ qua email này.</p>
          </div>
        `,
      });
    } catch (err) {
      throw new InternalServerErrorException('Không thể gửi email, vui lòng thử lại');
    }
  }
}