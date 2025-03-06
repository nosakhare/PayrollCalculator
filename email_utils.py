import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_payslip(self, recipient_email, employee_name, payslip_path, month_year):
        """Send payslip to employee via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f'Your Payslip for {month_year}'

            body = f"""
            Dear {employee_name},

            Please find attached your payslip for {month_year}.

            Best regards,
            HR Department
            """
            msg.attach(MIMEText(body, 'plain'))

            # Attach the payslip
            with open(payslip_path, 'rb') as f:
                pdf = MIMEApplication(f.read(), _subtype='pdf')
                pdf.add_header('Content-Disposition', 'attachment', 
                             filename=os.path.basename(payslip_path))
                msg.attach(pdf)

            # Send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)
