from jbrookerSquare.square_workday import SquareWorkday
import logging as log
import argparse
import re
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
    s.retrieve_workday_data(start_date=str(period['start_date']), end_date=str(period['end_date']))
