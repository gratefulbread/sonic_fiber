After downloading all the PDFs, Tabula () can be used to extract the tables:
`java -jar tabula-0.9.2-jar-with-dependencies.jar -b . -l -p all -r -u`
There's a lot of cruft in the CSVs, the important rows (Street, start and end intersections) can be found by looking for rows containing "RW :" in the 6th column.
The included Python script `clean_tabula_csv.py` can be run against all the CSVs which filters this rule, and adds the current street name to every first column.
After importing our CSV, the City's list of intersections and the City's street intersection geodata, we can do a few joins to get a list of points:
'''
SELECT a_points.the_geom, b_points.the_geom
FROM sonic_intersections
JOIN sf_intersections a ON sonic_intersections.street = a.streetname
  AND sonic_intersections.start = a.from_st
LEFT JOIN sf_intersections b ON sonic_intersections.street = b.streetname
  AND sonic_intersections.end = b.from_st
JOIN sf_intersection_points a_points ON a.CNN = a_points.CNN
LEFT JOIN sf_intersection_points b_points ON b.CNN = b_points.CNN
'''

I could install PostgreSQL or even SpatiaLite to generate proper geospatial data, but it's easier tojust mangle the WKT in place. Lines with two points will be drawn as lines while single points remain as dots.

`| sed -e 's/POINT (\(.*\))|POINT (\(.*\))/LINESTRING \(\1,\2\)/' | sed -e 's/|//'`
