import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    username = "habitattalk@gmail.com"
    password = "chxbmetaohxlassf"
    
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = "hakeemabdullah87@gmail.com"  # Replace with a valid recipient email
    msg['Subject'] = "Test Email"
    
    body = "This is a test email."
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(username, password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.close()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_test_email()
