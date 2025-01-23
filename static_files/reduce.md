mapshaper reduced-lrs.geojson -simplify dp 10% -o reduced-mapshaper-lrs.geojson
mapshaper reduced-lrs.geojson -simplify dp 10% -o format=geojson precision=0.001 reduced-mapshaper-lrs.geojson
mapshaper reduced-counties.geojson -simplify dp 10% -o reduced-mapshaper-counties.geojson
mapshaper reduced-counties.geojson -simplify dp 10% -o format=geojson preciison=0.001 reduced-mapshaper-counties.geojson
mapshaper reduced-counties.geojson -simplify dp 10% -o format=geojson preciison=0.001 Chesapeake_Bay_Watershed_Boundary.geojson.geojson
