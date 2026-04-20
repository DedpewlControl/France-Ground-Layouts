import json
from dms2dec import dec2dms_func

mode = 'labels'    # can be geo, labels or regions
geo_selection = ['LFST']  # exact match
regions_selection = ['LFST']    # if string is contained in feature name
labels_selection = ['LFST']     # if string is contained in feature name


def geo():
    with open('source/geo.geojson') as source:
        geo = json.load(source)
        for item in geo_selection:
            output_file = 'output/geo_{}.txt'.format(item).replace(' ', '_')
            w_edge_cnt = 0
            line_cnt = 0
            with open(output_file, 'w') as output:
                # write first line
                output.write('[GEO] {}'.format(item))
                output.write('\n')

                for feature in geo['features']:
                    pair_list = []
                    if feature['properties']['name'] == item:  # if selected

                        # fetch coordinates and convert to lists
                        coordinates = feature['geometry']['coordinates']
                        if len(coordinates) == 1:
                            if len(coordinates[0]) > 2:
                                for i, j in enumerate(coordinates[0][:-1]):
                                    pair = [j, coordinates[0][i + 1]]
                                    pair_list.append(pair)
                                feature['geometry']['coordinates'] = pair_list

                for feature in geo['features']:
                    # polygon properties
                    poly_name = feature['properties']['name']
                    poly_color = feature['properties']['color']
                    polygon_properties = [poly_color, poly_name]
                    if feature['properties']['name'] == item:

                        # polygon coordinates
                        dms_coord = []
                        for edge in feature['geometry']['coordinates']:
                            dms_edge = []
                            for vertex in edge:
                                dms_vertex = dec2dms_func(vertex)  # turn vertexes into DMS
                                dms_edge.append(dms_vertex)
                            dms_coord.append(dms_edge)

                        # format sct strings
                        for edge in dms_coord:
                            w_edge_cnt += 1
                            output.write('{} {} {} {} {}'.format(edge[0][1], edge[0][0], edge[1][1], edge[1][0],
                                                                 polygon_properties[0]))
                            output.write('\n')

        print('file saved to: {}'.format(output_file))
        print('written edges: {}'.format(w_edge_cnt))


def regions():
    # init counts
    vertexcnt = 0
    poly_cnt = 0

    # import geojson file
    with open('source/regions.geojson') as source:
        regions = json.load(source)

        for airport in regions_selection:
            # write to text file
            output_file = 'output/regions-{}.txt'.format(airport).replace(' ', '_')
            with open(output_file, 'w') as output:
                output.write('[REGIONS] {}'.format(airport))
                output.write('\n')

                for idx, feature in enumerate(regions['features']):
                    if airport in feature['properties']['name']:  # only output data for selected airport
                        coords = feature['geometry']['coordinates']

                        # Validate the coordinate structure
                        if not coords or not isinstance(coords[0], list) or not coords[0]:
                            print(f"⚠️  Skipping feature '{feature['properties']['name']}' at feature index {idx} (approx line ~{idx * 7 + 10}) due to missing or invalid coordinates.")
                            continue

                        poly_cnt += 1

                        # creating coordinate list in dms format
                        dmscoordset = []
                        for coordinate in coords[0][0]:
                            vertexcnt += 1
                            dmscoord = dec2dms_func(coordinate)
                            dmscoordset.append(dmscoord)

                        # remove repeated first vertex at the end from dmscoordset according to sct spec
                        if dmscoordset:
                            del dmscoordset[-1]

                        # output
                        output.write(feature['properties']['color'])
                        output.write('\n')
                        output.write('{} {} ;- {}'.format(dmscoordset[0][1], dmscoordset[0][0],
                                                          feature['properties']['name']))
                        output.write('\n')

                        del dmscoordset[0]
                        for vertex in dmscoordset:
                            output.write('{} {}'.format(vertex[1], vertex[0]))
                            output.write('\n')

                print('✅ File saved to: {}'.format(output_file))
                print('✏️  Written edges: {}'.format(vertexcnt))
                print('🧩 Polygons: {}'.format(poly_cnt))



def labels():
    with open('source/labels.geojson') as source:
        labels = json.load(source)
        for airport in labels_selection:
            label_cnt = 0
            # write to text file
            filename = 'output/labels-{}.txt'.format(airport)
            outputfile = open(filename, 'w')
            outputfile.write('[Labels] {}'.format(airport))
            outputfile.write('\n')

            for feature in labels['features']:
                if airport in feature['properties']['name']:
                    # polygon coordinates
                    vertex = feature['geometry']['coordinates']
                    dms_vertex = dec2dms_func(vertex)
                    outputfile.write('{} {} {} {}'.format(dms_vertex[1], dms_vertex[0], 
                                                          feature['properties']['text_label'], 
                                                          feature['properties']['color']))
                    outputfile.write('\n')
                    label_cnt += 1

            print('file saved to: {}'.format(filename))
            print('labels: {}'.format(label_cnt))


if __name__ == "__main__":
    if mode == 'geo':
        geo()
    elif mode == 'regions':
        regions()
    elif mode == 'labels':
        labels()
