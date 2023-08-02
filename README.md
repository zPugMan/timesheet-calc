# Timesheet Calc

Code to retrieve logged hours from Square. Logged hours are reported on a bi-monthly basis based on the provided `start_date` positional argument.

For example:
* `2023-07-01` - Retrieves all data from 7/1 to 7/15.
* `2023-07-16` - Retrieves all data from 7/16 to the end of the month, i.e. 7/31.

## Help
For help, include the `-h` argument.
```
usage: timesheet [-h] start_date

Retrieve the current time logged by employee for the start date desired

positional arguments:
  start_date  Start date to retrieve timesheet data

options:
  -h, --help  show this help message and exit
```  

## Execution
* Add an environment variable `SQUARE_ACCESS` with your assigned token provided by Square
* Invoke the code
```
python .\timesheet.py 2023-07-01
```

The result:
```
Employee   Day      start  end     total  reg   ot
--------------------------------------------------------------------------------
James D    Jul-01   09:54  18:22   8.47   8.00  0.47
James D    Jul-02   09:57  17:54   7.95   7.95  0.00
           Jul-03
           Jul-04
James D    Jul-05   09:58  17:59   8.02   8.00  0.02
James D    Jul-06   10:15  17:57   7.70   7.70  0.00
           Jul-07
James D    Jul-08   09:55  18:03   8.13   8.00  0.13
James D    Jul-09   09:54  18:06   8.20   8.00  0.20
           Jul-10
James D    Jul-11   10:06  17:09   7.05   7.05  0.00
James D    Jul-12   10:02  17:57   7.92   7.92  0.00
James D    Jul-13   10:31  18:12   7.68   7.68  0.00
           Jul-14
James D    Jul-15   09:49  17:56   8.12   8.00  0.12

Pay total ----------------------------------------------------------------------
James D                                  78.30   0.94
```