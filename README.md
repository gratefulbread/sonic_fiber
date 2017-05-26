# Sonic Fiber Map
This map is created from publicly-available permit data from http://bsm.sfdpw.org/reports/public/permitsearch.aspx
A search for "Sonic Telecom" as the Agency and "Temporary Occupancy" as the Permit Type returns a list of permits mostly associated with pulling aerial fiber up and down streets.
PDFs of the permits contain detailed street information and can be downloaded with the Print link next to each permit. `permiturls.txt` is a list of permit PDF urls as of May 22, 2017 and can be used to download all the PDFs within.
All of the following commands can be run in OS X and (probably) most Linux installs:
```
while read line; do curl -OJ $line; done < permiturls.txt
```

Once all the permits are downloaded, they can be run through tabula-extractor (https://github.com/tabulapdf/tabula-extractor) to try and convert the info to CSVs:
```
java -jar tabula-0.9.2-jar-with-dependencies.jar -b . -l -p all -r -u
```

There's a lot of cruft in the CSVs, but the important rows (street, start and end intersections) can be found by looking for rows containing "RW :" in the 6th column.
The included Python script `clean_tabula_csv.py` can be run against all the CSVs and filters lines by this rule while adding the current street name to every first column:
```
echo "streetname,from_st,to_st" > sonic_intersections.csv
for file in *.csv; do python clean_tabula_csv.py $file; done >> sonic_intersections.csv
```

The city of San Francisco provides street intersection data at data.sfgov.org. I used their List of Streets and Intersections (https://data.sfgov.org/Geographic-Locations-and-Boundaries/List-of-Streets-and-Intersections/pu5n-qu5c) and Street Intersections (https://data.sfgov.org/Geographic-Locations-and-Boundaries/Street-Intersections/ctsg-7znq) datasets. The List of Streets contains every intersection of every street in the City by name while the Street Intersections data contains the longitude and latitude of these intersections by "CNN" or "Centerline Network Number(?)". Exporting both sets from data.sfgov.org as CSVs, I imported them and our permit CSV into a sqlite database:
```
echo "
.separator ','
.import sonic_intersections.csv sonic_intersections
.import List_of_Streets_and_Intersections.csv sf_intersections
.import street_intersections.csv sf_intersection_points
" | sqlite3 sonic.sqlite
```

After importing our CSVs, we can do a few joins to get a list of points. I could have used PostgreSQL or SpatiaLite to generate proper geospatial data, but it's easier to just change the WKT point pairs to WKT linestrings in place:
```
echo "
SELECT DISTINCT a_points.the_geom, b_points.the_geom
FROM sonic_intersections
JOIN sf_intersections a ON sonic_intersections.streetname = a.streetname
  AND sonic_intersections.from_st = a.from_st
JOIN sf_intersections b ON sonic_intersections.streetname = b.streetname
  AND sonic_intersections.to_st = b.from_st
JOIN sf_intersection_points a_points ON a.CNN = a_points.CNN
JOIN sf_intersection_points b_points ON b.CNN = b_points.CNN;
" | sqlite3 sonic.sqlite | sed -e 's/POINT (\(.*\))|POINT (\(.*\))/LINESTRING \(\1,\2\)/' > sonic_fiber.wkt
```

The included `index.html` contains a basic Leaflet (https://leafletjs.com) map and Wicket (https://github.com/arthur-e/Wicket) plugin to parse and draw sonic_fiber.wkt.
The lines aren't perfect as the SQL query doesn't necessarily pick the right side or end of some streets, and I'm not using the City's CNN shapefile to follow the roads exactly, but it's a quick and dirty way of getting an idea of Sonic's fiber deployment.
Permits are being issued and executed every week and the data within is recent as of May 22, 2017.
