from square.client import Client
import os
import logging as log
from datetime import datetime

class SquareWorkday:
    ITEM_URL = {
                'sandbox':'https://squareupsandbox.com/dashboard/items/library/',
                'production':'https://squareup.com/dashboard/items/library/'
                }
    def retrieve_workday_data(self, start_date: str):
        log.info("Opening connection to environment: %s", self.environment)
        log.info("calling search...")
        result = self.client.labor.search_shifts(body = {"query": {"filter": { "start": { "start_at": "2023-05-16T00:00:00Z"}},"sort": {"field":"START_AT","order":"ASC"}}})

        if result.is_success():
            shift_data = []
            emp_lkup = self.get_employees()
            for shift in result.body['shifts']:
                shift_rec = {'start': shift['start_at'], 'end': shift['end_at'], 'employee': emp_lkup[shift['employee_id']]}
                self.check_shift(shift=shift_rec)
                shift_data.append(shift_rec)
            shift_data.reverse()
            log.info(shift_data)
        else:
            log.error("Failed to retrieve workday data.")
            log.error(result)

    def check_shift(self, shift: dict):
        start = datetime.fromisoformat(shift['start'])
        end = datetime.fromisoformat(shift['end'])
        err = (start.day == end.day)
        if err:
            log.info("%-20s        %s  %s %10s", shift['employee'], start, end, "OK")
        else:
            log.info("%-20s        %s  %s %10s", shift['employee'], start, end, "ERROR")
            log.error("Failed clockout detected... please correct data.")
            exit(code="Failed Clockout!")


    def get_employees(self) -> dict:
        log.info("Retrieving employees..")
        log.info(self.client)
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
        
    def __init__(self, environment = None|str):
        log.basicConfig(level = log.INFO)
        if environment == None:
            self.environment = 'sandbox'
        else:
            self.environment = environment

        toke = os.environ.get("SQUARE_ACCESS")
        if toke == None:
            log.error("Missing environment setting 'SQUARE_ACCESS' which is required for connectivity. Please set before executing.")
        
        self.client = Client(access_token = toke, environment = self.environment)
        
