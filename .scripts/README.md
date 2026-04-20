# SectorShape-Converter
Tool to convert [GNG sector files](http://gng.aero-nav.com/) for use with the VATSIM network to the GeoJSON format (and back again).

**To convert SCT to GeoJSON:**
1) Save your GNG SCT file to sct-source/ and change the file extension to .txt
2) Check if the filename in the python script matches your file and run importregion.py
3) GeoJSON output is saved to importregion-out/ as separate parts. 

**To convert GeoJSON to SCT:**
1) Save your edits as GeoJSON files including properties to geojson-source/
    * column 1 = ID
    * column 2 = name
    * column 3 = color (according to color definition in ";AutoCAD color definitions")
    * column 4 = editor (name of the person editing for easy management of coop-projects)
2) As with the import, check the filenames in the python scripts and run one of the following:
    * export_regions.py
    * export_geo.py
    * export_labels.py
3) SCT output is saved to exportregion-out

**Supported SCT sections**
* REGIONS - [MultiPolygon](https://en.wikipedia.org/wiki/GeoJSON)
* GEO - [MultiLineString](https://en.wikipedia.org/wiki/GeoJSON)                
* LABELS - [Point](https://en.wikipedia.org/wiki/GeoJSON)
* ARTCC_LOW (partially) - [MultiLineString](https://en.wikipedia.org/wiki/GeoJSON)