"""
Email sender for AI news digests
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailSender:
    """Send email digests via SMTP"""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_html_email(self, recipient_email: str, subject: str, html_content: str,
                       text_content: Optional[str] = None) -> bool:
        """
        Send an HTML email with optional plain text fallback
        Returns True if successful, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email

            # Add plain text version (if provided)
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_digest(self, recipient_email: str, html_content: str,
                   date_str: Optional[str] = None) -> bool:
        """Send a weekly digest email"""
        if date_str:
            subject = f"AI News Digest - {date_str}"
        else:
            subject = "AI News Digest - Weekly Update"

        return self.send_html_email(recipient_email, subject, html_content)
