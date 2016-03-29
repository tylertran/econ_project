#
# Data must start on 1/1/16 and be sorted by instance type
# and then by timestamp.
#
import sys
import re

ECON_DATA = sys.argv[1]
HEADERS = {}

with open(ECON_DATA, 'r') as econ_data:
    # First line is HEADERS
    row = econ_data.readline()
    for i, name in enumerate(row.split(',')):
        HEADERS[name.rstrip().upper()] = i

    output = open("%s_no_dec.csv" % ECON_DATA[:-4], 'w')

    output.write(row) # Write headers

    for row in econ_data:
        row_vals = row.split(',')

        # If current row's date is 12-31, change date to 2016-01-01,
        #   time to 00:00:00, sec to 0, hour to 1, qhour to 1
#        if row_vals[HEADERS['DATE']] == '2015-12-31':
#            row_vals[HEADERS['DATE']]  = '2016-01-01'
#            row_vals[HEADERS['TIME']]  = '00:00:00'
#            row_vals[HEADERS['SEC']]   = '0'
#            row_vals[HEADERS['HOUR']]  = '1'
#            row_vals[HEADERS['QHOUR']] = '1\n'
#            output.write(','.join(row_vals))
        if not not re.compile("2015-12-31*").match(row_vals[HEADERS['TIMESTAMP']]):
            row_vals[HEADERS['TIMESTAMP']] = '2016-01-01T00:00:00.000Z'
            output.write(','.join(row_vals))
        else:
            output.write(row)

    output.close()
