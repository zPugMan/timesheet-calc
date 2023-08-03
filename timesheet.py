from jbrookerSquare.square_workday import SquareWorkday
import logging as log
import argparse
import re
import smtplib
import configparser
from email.message import EmailMessage
from datetime import date, timedelta


def get_workperiod(start: str) -> dict:
    if start == None:
        raise Exception("Start date expected, but was NONE") 
    
    start_dt = date.fromisoformat(start)
    if start_dt.day == 1:
        end_dt = date(start_dt.year, start_dt.month, 15)
    else:
        if start_dt.month==12:
            n_dt = date(start_dt.year+1,1,1)
        else:
            n_dt = date(start_dt.year, start_dt.month+1, 1)
            
        end_dt = n_dt - timedelta(days=1)

    return { "start_date": start_dt, "end_date": end_dt}

def string_date_format(value: str, pat=re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")):
    if not pat.match(value):
        raise argparse.ArgumentTypeError("Invalid value provided. Expecting format: yyyy-MM-dd")
    return value

def send_mail(body: str, subject: str):
    log.info("Retrieving SMTP properties")
    cfg = configparser.RawConfigParser()
    cfg.read('config.ini')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = cfg.get('MailProperties', 'fromaddr')
    msg['To'] = cfg.get('MailProperties','toaddrs')
    smtp_server = cfg.get('MailProperties','server_smtp')
    smtp_port = cfg.get('MailProperties','port_smtp')
    smtp_secret = cfg.get('MailProperties','password')
    msg.set_content(body)

    msg.add_alternative("""
    <html>
        <head></head>
        <body>
          <div>
          <p>Here's the latest time card(s) for the period.</p>
          <pre>{msg_body}</pre>
          </div>
          <br />
          <p>Login to run payroll: <a href="https://quickbooks.intuit.com/login/">click</a></p>
        </body>
    </html> 
    """.format(msg_body=body), subtype='html')

    server = None
    try:
        server = smtplib.SMTP_SSL(host=smtp_server, port=smtp_port)
        server.set_debuglevel(False)
        server.login(user=msg['From'], password=smtp_secret)
        log.info("Sending email")
        server.send_message(msg)
    except Exception:
        log.error("Exception during mail send\n", Exception)
    finally:
        if server != None:
            log.info("Quiting smtp connection")
            server.quit()

if __name__ == "__main__":

    parsr = argparse.ArgumentParser(
        prog="timesheet",
        description="Retrieve the current time logged by employee for the start date desired"
    )
    parsr.add_argument("start_date", type=string_date_format, help="Start date to retrieve timesheet data")
    args = parsr.parse_args()

    period = get_workperiod(args.start_date)

    log.basicConfig(level = log.INFO)
    log.info("Retrieving logged work schedules: " + str(period['start_date']) + " to " + str(period['end_date']))

    s = SquareWorkday(environment='production')
    time_report = s.retrieve_workday_data(start_date=str(period['start_date']), end_date=str(period['end_date']))

    send_mail(body=time_report, subject=f"Time Report: {period['start_date']} - {period['end_date']}")

    log.info("All done. Bye.")