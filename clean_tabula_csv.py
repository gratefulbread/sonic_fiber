import csv
import sys
with open(sys.argv[1], 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        for col in row:
            if col.startswith('RW'):
                if row[1] != "":                    
                    last_street = row[1]
                print "%s,%s,%s" % (last_street.replace("\r", " "), row[2].replace("\r", " "), row[3].replace("\r", " "))
                continue
