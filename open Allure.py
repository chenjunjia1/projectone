import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

sender_email = "jia9785361@163.com"
receiver_email = "recipient@example.com"

email_password = "Chenjunjia233.."
smtp_server = "smtp.163.com"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "Allure Report"

body = "Please find the attached Allure report."
msg.attach(MIMEText(body, "plain"))

attachment = open("allure-report.zip", "rb").read()  # 请确保报告文件存在
part = MIMEApplication(attachment)
part.add_header("Content-Disposition", "attachment", filename="allure-report.zip")
msg.attach(part)

try:
    server = smtplib.SMTP(smtp_server, 25)
    server.starttls()
    server.login(sender_email, email_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Email sent successfully")
except Exception as e:
    print(f"Email could not be sent: {str(e)}")
