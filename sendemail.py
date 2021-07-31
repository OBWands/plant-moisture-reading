def send_alert_email(email_subject):
    import smtplib
    from configparser import ConfigParser
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE
    
    parser = ConfigParser()
    parser.read('./dev.ini')
    my_email = parser.get('email_settings', 'email_from')
    my_password = parser.get('email_settings', 'email_from_pass')
    to_email = parser.get('email_settings', 'email_to')
    smtp_server = parser.get('email_settings', 'email_server')
    smtp_port = parser.getint('email_settings', 'email_port')
    filename = parser.get('file_paths', 'pothos2_file_name')
    filepath = parser.get('file_paths', 'pothos2_file_path')
    
    subject = email_subject
    # Taking the latest moisture and temp readings from filepath
    with open(filepath, "r") as f1:
        last_line = f1.readlines()[-1]
        last_line_list = last_line.split(",")
    moisture = last_line_list[1]
    temp = last_line_list[2]
    body = (
			f"Here is the latest reading:\n\n"
            f"Moisture: {moisture}\n"
            f"Temperature: {temp}"
            )

    msg = MIMEMultipart()
    msg['From'] = my_email
    msg['To'] = COMMASPACE.join([to_email])
    msg['Subject'] = subject
    body = MIMEText(body)  # convert body to a MIME compatible string
    msg.attach(body)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filepath, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)
    
    smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
    smtp_obj.ehlo()
    smtp_obj.starttls()
    smtp_obj.login(my_email, my_password)
    smtp_obj.sendmail(my_email, to_email, msg.as_string())
    smtp_obj.quit()
    print("Email has been sent")

if __name__ == '__main__':
	from configparser import ConfigParser
	parser = ConfigParser()
	parser.read('./dev.ini')
	send_alert_email(parser.get('email_subject', 'status_update'))
