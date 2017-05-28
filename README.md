# Sonic Fiber Map
A map highlighting Sonic.net fiber deployments generated from publicly-available street permits.

## Demo
The map itself can be found at https://thatdan.github.io/sonic_fiber/

## Disclaimer
This map is purely speculative based on street permits. I have not verified whether Sonic's fiber service is available on every street highlighted.
To quote [samstave on HackerNews](https://news.ycombinator.com/item?id=14427548):
> Having the permit doesnt mean the fiber is pulled.

One can check addresses at https://www.sonic.com/availability

## TODO
- [x] Use street centerlines instead of intersecion points
- [ ] Add central office points
- [ ] Write single script for pulling/updating data
- [ ] Include permit number and date in map
- [ ] Add timelapse of permits

## How To
Permit data can be found at http://bsm.sfdpw.org/reports/public/permitsearch.aspx

A search for "Sonic Telecom" as the Agency and "Temporary Occupancy" as the Permit Type returns a list of permits mostly associated with pulling aerial fiber up and down streets.

PDFs of the permits contain detailed street information and can be downloaded with the Print link next to each permit.

`permiturls.txt` is a list of permit PDF urls as of May 22, 2017 and can be used to download all the PDFs within.

All of the following commands can be run in OS X and (probably) most Linux installs:
```bash
while read line; do curl -OJ $line; done < permiturls.txt;
```

Once all the permits are downloaded, they can be run through [tabula-extractor](https://github.com/tabulapdf/tabula-extractor) to try and convert the info to CSVs:
```bash
java -jar tabula-0.9.2-jar-with-dependencies.jar -b . -l -p all -r -u;
```

There's a lot of cruft in the CSVs, but the important rows (street, start and end intersections) can be found by looking for rows containing "RW :" in the 6th column.

The included Python script `clean_tabula_csv.py` can be run against all the CSVs and filters lines by this rule while adding the current street name to every first column:
```bash
echo "streetname,from_st,to_st" > sonic_intersections.csv;
for file in *.csv; do python clean_tabula_csv.py $file; done >> sonic_intersections.csv;
```

The city of San Francisco provides street and intersection data at data.sfgov.org.
I used their [List of Streets and Intersections](https://data.sfgov.org/Geographic-Locations-and-Boundaries/List-of-Streets-and-Intersections/pu5n-qu5c) and [Basemap Street Centerlines](https://data.sfgov.org/Geographic-Locations-and-Boundaries/San-Francisco-Basemap-Street-Centerlines/7hfy-8sz8) datasets.
The List of Streets contains every intersection of every street in the City by name as printed in the permits while the Basemap contains street geometry by "CNN" which is referenced in the List of Streets.
Exporting both sets as CSVs, I imported them and our permit CSV into an sqlite database:
```bash
echo "
.separator ','
.import sonic_intersections.csv sonic_intersections
.import List_of_Streets_and_Intersections.csv sf_intersections
.import San_Francisco_Basemap_Street_Centerlines.csv sf_cnn
" | sqlite3 sonic.sqlite
```

After importing our CSVs, we can do a few joins to get the geometry of the streets covered by the permits. I could have used PostgreSQL or SpatiaLite to generate proper geospatial data, but it's easier to just use the WKT the City includes with their CNN data.
```bash
echo "
SELECT sf_cnn.geometry FROM sonic_intersections sonic
JOIN sf_intersections sf ON sonic.streetname = sf.streetname
  AND sonic.from_st = sf.from_st
  AND sonic.to_st = sf.to_st
JOIN sf_cnn ON sf.CNN = sf_cnn.cnn;
" | sqlite3 sonic.sqlite > sonic_fiber.wkt
```

The included `index.html` contains a basic [Leaflet](https://leafletjs.com) map with the [Wicket](https://github.com/arthur-e/Wicket) plugin to parse and draw sonic_fiber.wkt.

Permits are being issued and executed every week and the data within is recent as of May 22, 2017.
