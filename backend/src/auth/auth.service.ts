import {
  Injectable,
  BadRequestException,
  UnauthorizedException,
  NotFoundException,
} from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcryptjs';
import * as crypto from 'crypto';
import { User, UserDocument } from './user.schema';
import { BlacklistedToken, BlacklistedTokenDocument } from './token-blacklist.schema';
import { PasswordReset, PasswordResetDocument } from './password-reset.schema';
import { MailService } from './mail.service';
import {
  RegisterDto,
  LoginDto,
  ChangePasswordDto,
  ForgotPasswordDto,
  VerifyOtpDto,
} from './auth.dto';

@Injectable()
export class AuthService {
  constructor(
    @InjectModel(User.name)
    private userModel: Model<UserDocument>,
    @InjectModel(BlacklistedToken.name)
    private blacklistModel: Model<BlacklistedTokenDocument>,
    @InjectModel(PasswordReset.name)
    private resetModel: Model<PasswordResetDocument>,
    private jwtService: JwtService,
    private mailService: MailService,
  ) {}

  private generateToken(id: string): string {
    return this.jwtService.sign({ id });
  }

  // ── Đăng ký ──────────────────────────────────────────────
  async register(dto: RegisterDto) {
    const existing = await this.userModel.findOne({ email: dto.email });
    if (existing) throw new BadRequestException('Email đã tồn tại');

    const user = await this.userModel.create(dto);
    return {
      message: 'Đăng ký thành công',
      token: this.generateToken(user._id.toString()),
      user: { id: user._id, name: user.name, email: user.email, role: user.role },
    };
  }

  // ── Đăng nhập ────────────────────────────────────────────
  async login(dto: LoginDto) {
    const user = await this.userModel.findOne({ email: dto.email });
    if (!user) throw new UnauthorizedException('Email hoặc mật khẩu sai');

    const valid = await bcrypt.compare(dto.password, user.password);
    if (!valid) throw new UnauthorizedException('Email hoặc mật khẩu sai');

    if (!user.isActive) throw new UnauthorizedException('Tài khoản đã bị khoá');

    return {
      message: 'Đăng nhập thành công',
      token: this.generateToken(user._id.toString()),
      user: { id: user._id, name: user.name, email: user.email, role: user.role },
    };
  }

  // ── Lấy thông tin user hiện tại ──────────────────────────
  getMe(user: UserDocument) {
    return { user };
  }

  // ── Đổi mật khẩu ─────────────────────────────────────────
  async changePassword(userId: string, dto: ChangePasswordDto) {
    const user = await this.userModel.findById(userId);
    if (!user) throw new UnauthorizedException();

    const valid = await bcrypt.compare(dto.oldPassword, user.password);
    if (!valid) throw new BadRequestException('Mật khẩu cũ không đúng');

    user.password = dto.newPassword;
    await user.save();
    return { message: 'Đổi mật khẩu thành công' };
  }

  // ── Đăng xuất (blacklist token) ───────────────────────────
  async logout(token: string) {
    const decoded = this.jwtService.decode(token) as { exp: number };
    if (!decoded) throw new BadRequestException('Token không hợp lệ');

    const expiresAt = new Date(decoded.exp * 1000);
    await this.blacklistModel.updateOne(
      { token },
      { token, expiresAt },
      { upsert: true },
    );
    return { message: 'Đăng xuất thành công' };
  }

  // ── Kiểm tra token có bị blacklist không ─────────────────
  async isTokenBlacklisted(token: string): Promise<boolean> {
    const found = await this.blacklistModel.findOne({ token });
    return !!found;
  }

  // ── Quên mật khẩu → gửi OTP ──────────────────────────────
  async forgotPassword(dto: ForgotPasswordDto) {
    const user = await this.userModel.findOne({ email: dto.email });
    // Không tiết lộ email có tồn tại hay không (bảo mật)
    if (!user) return { message: 'Nếu email tồn tại, OTP đã được gửi' };

    // Xoá OTP cũ của email này
    await this.resetModel.deleteMany({ email: dto.email });

    // Tạo OTP 6 số
    const otp = crypto.randomInt(100000, 999999).toString();
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 phút

    await this.resetModel.create({ email: dto.email, otp, expiresAt });
    await this.mailService.sendOtp(dto.email, otp);

    return { message: 'Nếu email tồn tại, OTP đã được gửi' };
  }

  // ── Xác nhận OTP → đặt lại mật khẩu ─────────────────────
  async verifyOtp(dto: VerifyOtpDto) {
    const record = await this.resetModel.findOne({
      email: dto.email,
      otp:   dto.otp,
      used:  false,
    });

    if (!record) throw new BadRequestException('OTP không đúng hoặc đã hết hạn');
    if (record.expiresAt < new Date()) throw new BadRequestException('OTP đã hết hạn');

    const user = await this.userModel.findOne({ email: dto.email });
    if (!user) throw new NotFoundException('Tài khoản không tồn tại');

    user.password = dto.newPassword;
    await user.save();

    // Đánh dấu OTP đã dùng
    record.used = true;
    await record.save();

    return { message: 'Đặt lại mật khẩu thành công, vui lòng đăng nhập lại' };
  }
}