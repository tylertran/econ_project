#
# Data must start on 1/1/16 and be sorted by instance type
# and then by timestamp.
#
# Extra fields required: DATE, SEC (i.e. time in seconds for given day)
#
import sys

QUARTER_HOURS = range(0, 86400, 900) # Quarter hours of a day in seconds
ECON_DATA = sys.argv[1]
HEADERS = {}

with open(ECON_DATA, 'r') as econ_data:
    # First line is HEADERS
    prev_line = econ_data.readline()
    for i, name in enumerate(prev_line.split(',')):
        HEADERS[name.rstrip().upper()] = i

    SEC = HEADERS['SEC']

    # Figure out end of file
    econ_data.seek(0, 2)
    EOF = econ_data.tell()
    econ_data.seek(0, 0)
    econ_data.readline() # We already read first line earlier

    output = open("%s_filled.csv" % ECON_DATA[:-4], 'w')

    while econ_data.tell() != EOF:
        reset = False
        skip = False
        # "Pointer" to mark which quarter hour of the day to check for
        for qhour in QUARTER_HOURS:
            if reset:
                break
            # Keep reading through econ data
            while True:
                prev_pos = econ_data.tell()
                row = econ_data.readline()
                if not row:
                    break

                prev_line_vals = prev_line.split(',')
                vals = row.split(',')
                row_sec = int(vals[SEC])

                # If we've finished an instance type, then "reset"
                # Account for header row
                if prev_line_vals[HEADERS['INSTANCETYPE']] != 'InstanceType' and vals[HEADERS['INSTANCETYPE']] != prev_line_vals[HEADERS['INSTANCETYPE']]:
                    prev_line = row
                    reset = True
                    break

                # If this row's time == quarter hour, write prev and move to next qhour
                if row_sec == qhour:
                    output.write(prev_line)
                    prev_line = row
                    break
                # If this row's time in seconds > the quarter hour, write previous
                #     line with updated seconds field then move on to next qhour
                elif row_sec > qhour:
                    if not skip:
                        output.write(prev_line)
                    prev_line_vals[SEC] = qhour
                    # Also update date
                    prev_line_vals[HEADERS['DATE']] = vals[HEADERS['DATE']]
                    new_line = ','.join(str(e) for e in prev_line_vals)
                    output.write(new_line)
                    # If need to insert multiple new rows
                    if (row_sec - qhour >= 900):
                        # Set file pointer to previous line
                        econ_data.seek(prev_pos)
                        # No need to rewrite the previous line
                        skip = True
                        break
                    # If it's the end of the day
                    elif qhour == QUARTER_HOURS[-1]:
                        # Copy over the rest of the day's data
                        prev_line = row
                        while True:
                            prev_write = output.tell()
                            output.write(prev_line)

                            prev_pos = econ_data.tell()
                            row = econ_data.readline()
                            if not row: break

                            prev_line_vals = prev_line.split(',')
                            vals = row.split(',')
                            row_sec = int(vals[SEC])
                            if vals[HEADERS['DATE']] == prev_line_vals[HEADERS['DATE']] and row_sec > QUARTER_HOURS[-1]:
                                prev_line = row
                            else:
                                # Keep prev_line as prev_line
                                row = prev_line
                                # Back up a line to reset ourselves
                                econ_data.seek(prev_pos)
                                output.seek(prev_write)
                                break
                    skip = False
                    prev_line = row
                    break
                # If this row is still < the quarter hour write prev line
                else:
                    # If we still have qhours left but we've reached the end of the day's data
                    if prev_line_vals[HEADERS['DATE']] != vals[HEADERS['DATE']] and qhour != 0:
                        prev_line_vals[SEC] = qhour
                        new_line = ','.join(str(e) for e in prev_line_vals)
                        output.write(new_line)
                        econ_data.seek(prev_pos)
                        break
 
                    output.write(prev_line)

                prev_line = row

    output.close()
