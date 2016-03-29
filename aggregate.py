#
# Data must already be sorted by instance type then by timestamp
# Extra fields required:
#     SEC, DURATION, DATE, HOUR, QHOUR, DAY (in month?)
#
import sys

HEADERS = {} # Top row of CSV
ECON_DATA = sys.argv[1]
AGGREGATE = sys.argv[2].upper()

with open(ECON_DATA, 'r') as econ_data:
    # First line is HEADERS
    row = econ_data.readline().rstrip()
    for i, name in enumerate(row.split(',')):
        HEADERS[name.upper()] = i

    # Write row with new column to output file
    # Output file is name of data file (minus .csv) + some stuff
    output = open(ECON_DATA[:-4] + '_agg_' + AGGREGATE + '.csv', 'w')
    output.write(row + ',AVG_SP\n')

    # First row of data is a special case...
    row = econ_data.readline()
    vals = row.split(',')
    curr_agg = vals[HEADERS[AGGREGATE]]
    output.write(row.rstrip())
    duration = int(vals[HEADERS['DURATION']])
    spot_price = float(vals[HEADERS['SPOTPRICE']])
    acc = spot_price * duration # Sum (accumulator) of spot price on curr_agg
    count = duration # Number of spot prices read for curr_agg

    # Process the rest of the data
    for row in econ_data:
        vals = row.split(',')
        this_agg = vals[HEADERS[AGGREGATE]]
        duration = int(vals[HEADERS['DURATION']])
        spot_price = float(vals[HEADERS['SPOTPRICE']])

        if this_agg != curr_agg:
            # Set new val for aggregation
            curr_agg = this_agg
            # Append avg to new file (timestamp is irrelevant)
            #     and add new line for new curr_agg
            output.write(",%f\n%s" % (acc/count, row.rstrip()) )
            # Start sum for new curr_agg and reset count
            acc = spot_price * duration
            count = duration
        else:
            # This row's spot price goes into the current sum
            acc += (spot_price * duration)
            count += duration

    # Last line/date is also special case
    output.write(",%f" % (acc/count) )

    output.close()
