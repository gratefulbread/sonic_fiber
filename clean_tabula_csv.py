import csv
import sys
file = sys.argv[1]
with open(sys.argv[1], 'rb') as f:
    permit = file.replace("_StreetUsePermit.csv", "")
    reader = csv.reader(f)
    for row in reader:
        for col in row:
            if col.startswith('RW'):
                if row[1] != "":                    
                    last_street = row[1]
                # permit,streetname,from_st,to_st
                print "%s,%s,%s,%s" % (permit, last_street.replace("\r", " "), row[2].replace("\r", " "), row[3].replace("\r", " "))
                continue
