from square.client import Client
import os
import logging as log
import calendar
from datetime import datetime,timedelta

class SquareWorkday:
    ITEM_URL = {
                'sandbox':'https://squareupsandbox.com/dashboard/items/library/',
                'production':'https://squareup.com/dashboard/items/library/'
                }
    def retrieve_workday_data(self, start_date: str, end_date: str) -> str:
        log.info("Opening connection to environment: %s", self.environment)
        end_date = datetime.fromisoformat(end_date)
        start = start_date + "T00:00:00Z"
        end = str(end_date.date() + timedelta(1)) + "T00:00:00Z"
        log.info(f"calling search...{start} - {end}")
        result = self.client.labor.search_shifts(body = {"query": {"filter": { "start": { "start_at": start, "end_at": end}},"sort": {"field":"START_AT","order":"ASC"}}})

        if result.is_success():
            shift_data = []
            emp_lkup = self.get_employees()
            for shift in result.body['shifts']:
                if shift['status']=='CLOSED':
                    shift_rec = {'start': datetime.fromisoformat(shift['start_at']), 'end': datetime.fromisoformat(shift['end_at']), 'employee': emp_lkup[shift['employee_id']], 'timecard_status': shift['status']}
                elif shift['status']=='OPEN':
                    shift_rec = {'start': datetime.fromisoformat(shift['start_at']), 'end': '', 'employee': emp_lkup[shift['employee_id']], 'timecard_status': shift['status']}
                else:
                    log.warn('Shift with start:' + shift['start_at'] +' is showing unexpected status: ' + shift['status'])

                # self.log_shift(shift=shift_rec)
                shift_data.append(shift_rec)
            shift_data.reverse()
        else:
            log.error("Failed to retrieve workday data.")
            log.error(result)

        # print(shift_data)
        result = self.get_report(report_start=datetime.fromisoformat(start_date)
                        , report_end=end_date
                        , data=shift_data)
        return result
        

    def log_shift(self, shift: dict):
        err = False
        # start = datetime.fromisoformat(shift['start'])
        start = shift['start']

        if shift['timecard_status'] == 'CLOSED':
            # end = datetime.fromisoformat(shift['end'])
            end = shift['end']
            err = not (start.day == end.day)
            normal_time = clock_time = round((end - start).seconds / 3600, 2)
            ot_time = 0
            if clock_time > 8:
                normal_time = 8
                ot_time = round(clock_time - normal_time,2)
        else:
            end = None

        if not err:
            log.info(f"{shift['employee']:10s} {start:%b-%d}   {start:%H:%M}  {end:%H:%M} {clock_time:5.2}    {normal_time:4}   {ot_time:4}")
        else:
            log.info("%-20s        %s  %s %10s", shift['employee'], start, end, "ERROR")
            log.error("Failed clockout detected... please correct data.")

    def get_report(self, report_start:datetime.date, report_end:datetime.date, data=[]) -> str:
        log.info("Finalized report")
        cal = calendar.Calendar()
        days = cal.itermonthdates(report_start.year, report_start.month)
        emp_list = []
        result = []

        result.append(f"{'Employee':10s} {'Day':5s}    {'start':5s}  {'end':5s}   {'total':5s}  {'reg':5s} {'ot':5s}")
        # print(f"{'Employee':10s} {'Day':5s}    {'start':5s}  {'end':5s}   {'total':5s}  {'reg':5s} {'ot':5s}")
        result.append(f"{'-'*80}")
        # print(f"{'-'*80}")
        for day in days:
            if day.month != report_start.month:
                # log.info(f"{day.month} != {report_start.month}: {day.month != report_start.month}")
                continue

            if report_start.day == 1 and day.day > 15:
                # log.info(f"1-15 check: {day}")
                continue
            elif report_start.day == 16 and day.day <= 15:
                # log.info(f"15+ check: {day}")
                continue
            else:
                # log.info(f"start day: {report_start.day} ; eval day: {day}")
                rec = list(filter(lambda r: r['start'].date() == day, data))
                if rec == []:
                    # print(f"{'':10s} {day:%b-%d}")
                    result.append(f"{'':10s} {day:%b-%d}")
                else:
                    shift = rec[0]
                    
                    start = shift['start']
                    end = shift['end']
                    if shift['employee'] not in emp_list:
                        emp_list.append(shift['employee'])
                    clock_time = round((end - start).seconds / 3600, 2)
                    shift['normal_time'] = float(clock_time)
                    shift['ot_time'] = 0
                    if clock_time > 8:
                        shift['normal_time'] = 8.00
                        shift['ot_time'] = round(clock_time - shift['normal_time'],2)
                    # log.info(shift)
                    # print(f"{shift['employee']:10s} {start:%b-%d}   {start:%H:%M}  {end:%H:%M}   {clock_time:.2f}   {shift['normal_time']:.2f}  {shift['ot_time']:.2f}")
                    result.append(f"{shift['employee']:10s} {start:%b-%d}   {start:%H:%M}  {end:%H:%M}   {clock_time:.2f}   {shift['normal_time']:.2f}  {shift['ot_time']:.2f}")
        # print("")
        result.append(f"Pay total {'-'*70}")
        # print(f"Pay total {'-'*70}")
        for emp in emp_list:
            emp_recs = list(filter(lambda rec: rec['employee']==emp, data))
            normal_time = sum(list(map(lambda rec: rec['normal_time'], emp_recs)))
            ot_time =  sum(list(map(lambda rec: rec['ot_time'], emp_recs)))
            # print(f"{emp:20s}                     {normal_time:.2f}   {ot_time:.2f}")
            result.append(f"{emp:20s}                     {normal_time:.2f}   {ot_time:.2f}")

        return '\n'.join(result)

    def get_employees(self) -> dict:
        log.info("Retrieving employees..")
        self.client = Client(access_token = os.environ.get("SQUARE_ACCESS"), environment = self.environment)
        result = self.client.team.search_team_members(body={"query":{"filter": {"status":"ACTIVE"}}})

        if result.is_success():
            log.info("Employee data retrieved")
            emp_list = {}
            for emp in result.body['team_members']:
                emp_list[emp['id']] = emp['given_name'] + ' ' + emp['family_name'][0]
            log.debug(emp_list)
            return emp_list
        else:
            log.error("Failed to retrieve employee data.")
            log.error(result)
            return
        
    def __init__(self, environment = None):
        log.basicConfig(level = log.INFO)
        if environment == None:
            self.environment = 'sandbox'
        else:
            self.environment = environment

        toke = os.environ.get("SQUARE_ACCESS")
        if toke == None:
            log.error("Missing environment setting 'SQUARE_ACCESS' which is required for connectivity. Please set before executing.")
            exit(code="SQUARE_ACCESS token required!")
        
        self.client = Client(access_token = toke, environment = self.environment)
        
