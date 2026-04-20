import json

feature_cnt = 0
filename = 'labels(1).geojson'

with open('geojson-source/{}'.format(filename)) as geojson_source:
    data = json.load(geojson_source)
    for x in data['features']:
        feature_cnt += 1
        x['properties']['id'] = feature_cnt

    name = 'id_fix_out/idfixed_{}'.format(filename)
    output_file = open(name, 'w')
    output_file.write(json.dumps(data, indent=4))
    # print(json.dumps(basedict, indent=4))
    output_file.close()
    print_string = 'GeoJSON saved to {}'.format(name)
    print(print_string)
