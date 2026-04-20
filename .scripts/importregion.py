'''open dependencies'''
import json
from gj_parser_func import region_p, artcc_p, geo_p, labels_p, sct_splitter

'''init vars'''

features = []
feature_id = 0

'''import text file '''
# f = open('sct-source/EHAA-EuroScope_20200424160817-200501-0002.txt', 'r')  TODO: file location
f = open('sct-source/import_gng_CUR2.txt', 'r')

'''process lines & split into sections'''
data = f.read()
sct_dictionary = sct_splitter(data)
sct_dictionary = [feature_id, sct_dictionary]

'''PARSE VORs'''
# VOR_lines = split_sct['VOR'].split('/n')
# for line in VOR_lines:
# 	print(line)

'''PARSE REGIONS'''
gj_region = region_p(sct_dictionary)
sct_dictionary[feature_id] = gj_region[0]  # extract feature_id
features.append(gj_region)

'''PARSE (/LOW)ARTCC'''
gj_artcc = artcc_p(sct_dictionary)
sct_dictionary[feature_id] = gj_artcc[0]  # extract feature_id
features.append(gj_artcc)

'''PARSE GEO    NOTE: Different Colors should be grouped together, and a group can only appear once'''
gj_geo = geo_p(sct_dictionary)
sct_dictionary[feature_id] = gj_geo[0]  # extract feature_id
features.append(gj_geo)

'''parse labels'''
gj_labels = labels_p(sct_dictionary)
sct_dictionary[feature_id] = gj_labels[0]  # extract feature_id
features.append(gj_labels)

'''print counts'''
print("Feature-Count =", sct_dictionary[feature_id])

'''Create GeoJSON Header'''
for section in features:
    basedict = {}
    crsdict = {}
    propertydict = {}
    basedict['type'] = "FeatureCollection"
    basedict['name'] = ''
    propertydict['name'] = "urn:ogc:def:crs:OGC:1.3:CRS84"
    crsdict['type'] = "name"
    crsdict['properties'] = propertydict
    basedict['crs'] = crsdict
    basedict['features'] = section[1]

    '''write to text file'''
    name = section[2]
    outputfile = open('{}.geojson'.format(name), 'w')
    outputfile.write(json.dumps(basedict, indent=4))
    # print(json.dumps(basedict, indent=4))
    outputfile.close()
    print_string = 'GeoJSON saved to {}.geojson'.format(name)
    print(print_string)

'''close the region_part.txt file'''
f.close()