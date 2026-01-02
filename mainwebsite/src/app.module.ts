import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { LoggingService } from './logging.service';
import { ContactService } from './contact/contact.service';
import { AuthController } from './auth.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Contact } from './entities/contact.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '3306'),
      username: process.env.DB_USERNAME || 'root',
      password: process.env.DB_PASSWORD || 'password',
      database: process.env.DB_NAME || 'website',
      entities: [Contact],
      synchronize: process.env.NODE_ENV !== 'production',
    }),
    TypeOrmModule.forFeature([Contact]),
  ],
  controllers: [AppController, AuthController],
  providers: [LoggingService, ContactService],
})
export class AppModule {}
