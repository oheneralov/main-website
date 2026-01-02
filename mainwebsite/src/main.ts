import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';
import { join } from 'path';
import { LoggingService } from './logging.service';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  
  // Enable CORS for local development
  app.enableCors();

  // Serve static files from the 'public' directory (React app, assets, etc.)
  app.useStaticAssets(join(__dirname, '..', 'public'));

  // Use the custom logging service
  const loggingService = app.get(LoggingService);
  app.useLogger(loggingService);

  const port = process.env.PORT || 3000;
  await app.listen(port);
  console.log(`Application running on port ${port}`);
  console.log(`React frontend served from: http://localhost:${port}`);
}
bootstrap();

