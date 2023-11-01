from .jbrookerSquare.square_workday import SquareWorkday
import logging as log
import argparse
import os
import json
import re
import smtplib
import configparser
from email.message import EmailMessage
from datetime import date, datetime, timedelta
import time
import pytz

import azure.functions as func

def period_end(end: date) -> bool:
    if end == None:
        raise Exception("End date expected on period_end check..")
    
    next_day = end + timedelta(days=-1)
    
    if end.day == 16:
        return True
    elif end.day == 1:  #more UTC conversion confusion
        return True
    else:
        return False
    

def get_workperiod(end: str) -> dict:
    if end == None:
        raise Exception("End date expected, but was NONE")
    
    is_utc = True
    if time.tzname[0][0:7]=='Pacific':
        is_utc = False
    
    end_dt = datetime.fromisoformat(end)
    if is_utc:
        end_dt.replace(tzinfo=pytz.utc)    
    else:
        end_dt.astimezone(pytz.timezone('US/Pacific'))
        log.info(f"UTC conversion to 'US/Pacific': {end_dt}")

    if end_dt.day >= 1 and end_dt.day <=17:
        start_dt = date(end_dt.year, end_dt.month, 1)
        end_dt = date(end_dt.year, end_dt.month, 15)
    else:
        start_dt = date(end_dt.year, end_dt.month, 16)

    return { "start_date": start_dt, "end_date": end_dt}

def string_date_format(value: str, pat=re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")):
    if not pat.match(value):
        raise argparse.ArgumentTypeError("Invalid value provided. Expecting format: yyyy-MM-dd")
    return value

def send_mail(body: str, subject: str):
    log.info("Retrieving SMTP properties")
    # cfg = configparser.RawConfigParser()
    # cfg.read('config.ini')
    cfg = json.loads(os.getenv('smtpCredentials'))

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = cfg['fromaddr']
    msg['To'] = cfg['toaddrs']
    smtp_server = cfg['server_smtp']
    smtp_port = cfg['port_smtp']
    smtp_secret = cfg['password']
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

def exec(end_date: str) -> None:
    period = get_workperiod(end=end_date)

    log.basicConfig(level = log.INFO)
    log.info("Retrieving logged work schedules: " + str(period['start_date']) + " to " + str(period['end_date']))

    s = SquareWorkday(environment='production')
    time_report = s.retrieve_workday_data(start_date=str(period['start_date']), end_date=str(period['end_date']))

    print(f"{time_report}")
    send_mail(body=time_report, subject=f"Time Report: {period['start_date']} - {period['end_date']}")


def main(timesheetTimer: func.TimerRequest) -> None:
    now = date.today()
    log.info("Azure function initiated. " + str(now))    
    if period_end(now):
        exec(end_date=str(now))
    else:
        log.info(f"{now} not end of month.")
    # try:
    #     log.info(f"Square Token? {os.getenv('SQUARE_ACCESS')[0:10]}")
    # except Exception:
    #     log.error("Exception on Square Token", Exception)

    log.info("All done. Bye.")

def manual() -> None:
    log.info("Executing in manual mode..")
    parsr = argparse.ArgumentParser(
        prog="timesheet",
        description="Retrieve the current time logged by employee for the start date desired"
    )
    parsr.add_argument("start_date", type=string_date_format, help="Start date to retrieve timesheet data", default=date.today())
    args = parsr.parse_args()

    exec(end_date=args.start_date)

# if __name__ == "__main__":
#     logger = log.getLogger()
#     logger.addHandler(hdlr=log.StreamHandler())
#     logger.setLevel(level=log.DEBUG)
#     main()