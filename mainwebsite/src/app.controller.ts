import { Controller, Get, Post, Body } from '@nestjs/common';
import sgMail from '@sendgrid/mail';
import { ContactService } from './contact/contact.service';
import { LoggingService } from './logging.service';

@Controller()
export class AppController {
  constructor(
    private readonly contactService: ContactService,
    private readonly loggingService: LoggingService,
  ) {}

  @Get()
  getIndex() {
    return { message: 'Welcome to AWS Info Website API' };
  }

  private async sendMail(name: string, email: string, message: string): Promise<void> {
    sgMail.setApiKey(process.env.SENDGRID_API_KEY || '');

    const msg = {
      to: process.env.CONTACT_EMAIL || 'admin@example.com',
      from: process.env.SENDER_EMAIL || 'noreply@example.com',
      replyTo: email,
      subject: `Contact Form: ${name}`,
      text: message,
      html: `<strong>Name:</strong> ${name}<br><strong>Message:</strong> ${message}`,
    };

    try {
      await sgMail.send(msg);
      this.loggingService.log(`Email sent successfully from ${email}`);
    } catch (error) {
      this.loggingService.error(`Error sending email: ${error}`, error.stack);
    }
  }
  

  @Post('contacts')
  async handleContactForm(@Body() body: any) {
    const { name, email, message } = body;

    if (!name || !email || !message) {
      return { success: false, message: 'Missing required fields' };
    }

    try {
      // Save contact to database
      await this.contactService.createContact(name, email, message);
      
      // Send email notification
      await this.sendMail(name, email, message);
      
      this.loggingService.log(`Contact form submitted by ${email}`);
      return { success: true, message: 'Contact saved successfully' };
    } catch (error) {
      this.loggingService.error(`Error processing contact form: ${error}`, error.stack);
      return { success: false, message: 'Error processing form' };
    }
  }
}


