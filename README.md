# Sonic Fiber Map
A map highlighting Sonic.net fiber deployments generated from publicly-available street permits. Basis is from ThatDan/sonic_fiber
Data is currently excavation permits, rather than the temporary occupancy permits that were on Dan's map.

## Demo
The map itself can be found at https://gratefulbread.github.io/sonic_fiber/

## Disclaimer
This map is purely speculative based on street permits. I have not verified whether Sonic's fiber service is available on every street highlighted.
To quote [samstave on HackerNews](https://news.ycombinator.com/item?id=14427548):
> Having the permit doesnt mean the fiber is pulled.

One can check addresses at https://www.sonic.com/availability

## Changelog

### 2017-08-17
- Including Leaflet to prevent CDN issues.
- Manually fixing "COLLINGWO OD" issue for now.

### 2017-08-08
- Waited for some permits to collect before updating. Biggest ones are for 19th St, Douglas St, Clipper St, 26th St, and Cesar Chavez St. Some permits are for underground conduit checks (e.g. 17TOC-4689 in Excelsior) which might hint to future plans.

## TODO
- [ ] Write single script for pulling/updating data
- [ ] and date on map
- [ ] Add timelapse of permits
- [ ] Add different color scheme for different permit types.
- [ ] Investigate if other permits are being processed by other named applicants. i.e. 3rd party contractors.

## How To
Permit data can be found at http://bsm.sfdpw.org/reports/public/permitsearch.aspx

A search for "Sonic Telecom" as the Agency and "Temporary Occupancy" as the Permit Type returns a list of permits mostly (but not always) associated with pulling aerial fiber up and down streets.

PDFs of the permits contain detailed street information and can be downloaded with the Print link next to each permit. Any number of plugins or tools can be used to download these en masse.

Once all the permits are downloaded, they can be run through [tabula-java](https://github.com/tabulapdf/tabula-java) to convert the info into CSVs:
```bash
java -jar tabula-0.9.2-jar-with-dependencies.jar -b . -l -p all -r -u;
```

There's a lot of cruft in the CSVs, but the important rows (street, start and end intersections) can be found by looking for rows containing "RW :" in the 6th column.

The included Python script `clean_tabula_csv.py` can be run against all the CSVs and filters lines by this rule while adding the current street name to every first column:
```bash
echo "permit,streetname,from_st,to_st" > sonic_intersections.csv;
ls 1*TOC*.csv | xargs -L1 python clean_tabula_csv.py >> sonic_intersections.csv;
```

The city of San Francisco provides street and intersection data at data.sfgov.org.
I used their [List of Streets and Intersections](https://data.sfgov.org/Geographic-Locations-and-Boundaries/List-of-Streets-and-Intersections/pu5n-qu5c) and [Basemap Street Centerlines](https://data.sfgov.org/Geographic-Locations-and-Boundaries/San-Francisco-Basemap-Street-Centerlines/7hfy-8sz8) datasets.
The List of Streets contains every intersection of every street in the City by name as printed in the permits while the Basemap contains street geometry by "CNN" which is referenced in the List of Streets.
Exporting both sets as CSVs, I imported them and our permit CSV into an sqlite database:
```bash
rm sonic.sqlite;
echo "
.separator ','
.import sonic_intersections.csv sonic_intersections
.import List_of_Streets_and_Intersections.csv sf_intersections
.import San_Francisco_Basemap_Street_Centerlines.csv sf_cnn
" | sqlite3 sonic.sqlite
```

After importing our CSVs, we can do a few joins to get the geometry of the streets covered by the permits. I could have used PostgreSQL or SpatiaLite to generate proper geospatial data, but it's easier to just use the [WKT](https://en.wikipedia.org/wiki/Well-known_text) the City includes with their CNN data.
```bash
echo "
SELECT sf_cnn.cnn, sonic.permit, sonic.streetname, sonic.from_st, sonic.to_st, sf_cnn.geometry
FROM sonic_intersections sonic
LEFT JOIN sf_intersections sf
  ON sonic.streetname = sf.streetname
  AND sonic.from_st = sf.from_st
  AND sonic.to_st = sf.to_st
LEFT JOIN sf_cnn
  ON sf.cnn = sf_cnn.cnn;
" | sqlite3 sonic.sqlite > sonic_fiber.csv
```

The included `index.html` contains a basic [Leaflet](https://leafletjs.com) map with the [Wicket](https://github.com/arthur-e/Wicket) plugin to parse and draw `sonic_fiber.csv`.

## Central Office Locations
Per a [request from phillijw](https://github.com/ThatDan/sonic_fiber/issues/1) I added markers highlighting Sonic's central offices as found in [this post from Dane Jasper](https://forums.sonic.net/viewtopic.php?f=10&t=2537&hilit=bonding&sid=439789da503651643b058d62747776b2&start=20#p16177). A CSV with coordinates is in `sonic_cos.csv`.
