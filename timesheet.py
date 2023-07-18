from jbrookerSquare.square_workday import SquareWorkday
import logging as log

# def get_workday():


if __name__ == "__main__":
    log.basicConfig(level = log.INFO)
    log.info("Retrieving logged work schedules")

    s = SquareWorkday(environment='production')
    s.retrieve_workday_data(start_date='2023-07-01', end_date='2023-07-15')
