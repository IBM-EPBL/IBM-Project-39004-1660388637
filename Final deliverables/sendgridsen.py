from sendgrid import SendGridAPIClient, Mail

def sendmail(rec):
    api_key =  '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'
    message = Mail(
        from_email='rrsamy1359@gmail.com',
        to_emails=rec,
        subject='welcome to fashunn',
        html_content='<strong>YOU HAVE CREATED AN ACCOUNT IN FASHUNN SUCCESSFULLY</strong>')
    try:

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        print('sendddmeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    except Exception as e:
        print("errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        print(e.message)
