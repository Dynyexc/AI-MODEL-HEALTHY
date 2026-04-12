import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { ConfigService } from '@nestjs/config';
import { Request } from 'express';
import { User, UserDocument } from './user.schema';
import { BlacklistedToken, BlacklistedTokenDocument } from './token-blacklist.schema';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    @InjectModel(User.name)
    private userModel: Model<UserDocument>,
    @InjectModel(BlacklistedToken.name)
    private blacklistModel: Model<BlacklistedTokenDocument>,
    config: ConfigService,
  ) {
    super({
      jwtFromRequest:   ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey:      config.get<string>('JWT_SECRET', 'secret'),
      passReqToCallback: true,
    });
  }

  async validate(req: Request, payload: { id: string }) {
    // Lấy raw token từ header
    const token = req.headers.authorization?.split(' ')[1];

    // Kiểm tra token có bị blacklist không
    if (token) {
      const blacklisted = await this.blacklistModel.findOne({ token });
      if (blacklisted) throw new UnauthorizedException('Token đã hết hiệu lực, vui lòng đăng nhập lại');
    }

    const user = await this.userModel.findById(payload.id).select('-password');
    if (!user) throw new UnauthorizedException();
    if (!user.isActive) throw new UnauthorizedException('Tài khoản đã bị khoá');

    return user;
  }
}