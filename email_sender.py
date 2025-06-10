import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import os
from config import CSV_FILE_PATH

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.df = None
        self.load_leads()

    def load_leads(self):
        """Load leads from CSV file and add email_status column if it doesn't exist"""
        self.df = pd.read_csv(CSV_FILE_PATH)
        if 'email_status' not in self.df.columns:
            self.df['email_status'] = 'Not Sent'
            self.df['email_sent_date'] = None
            self.save_leads()

    def save_leads(self):
        """Save leads back to CSV file"""
        self.df.to_csv(CSV_FILE_PATH, index=False)

    def send_email(self, recipient_email, recipient_name, subject, body):
        """Send an email to a recipient"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")
            return False

    def process_leads(self, limit=450):
        """Process leads and send emails up to the specified limit"""
        unsent_leads = self.df[self.df['email_status'] == 'Not Sent']
        processed_count = 0

        for index, lead in unsent_leads.iterrows():
            if processed_count >= limit:
                break

            # Customize email content based on lead's role
            subject = f"Connecting with {lead['name']} - {lead['role']}"
            body = f"""Dear {lead['name']},

I hope this email finds you well. I noticed your impressive work as a {lead['role']} at {lead['company']}.

[Your personalized message here]

Best regards,
[Your name]"""

            if self.send_email(lead['email'], lead['name'], subject, body):
                self.df.at[index, 'email_status'] = 'Sent'
                self.df.at[index, 'email_sent_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_leads()
                processed_count += 1
                print(f"Successfully sent email to {lead['email']}")
            
            # Add a delay between emails to avoid being marked as spam
            time.sleep(2)

        print(f"Processed {processed_count} leads")

def main():
    # Email configuration
    SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
    SMTP_PORT = 587  # Replace with your SMTP port
    SENDER_EMAIL = ""  # Replace with your ema
    SENDER_PASSWORD = ""  # Replace with your email password or app password

    # Create email sender instance
    sender = EmailSender(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD)
    
    # Process leads with a limit of 450
    sender.process_leads(limit=450)

if __name__ == "__main__":
    main() 