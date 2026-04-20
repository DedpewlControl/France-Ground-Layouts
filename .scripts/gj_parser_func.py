from dms2dec import dms2dec_func


def region_p(sct_dictionary):  # parser for the [REGIONS] Section
    feature_id = sct_dictionary[0]
    other_vertex_count = 0
    polygon = None
    feature_type = 'MultiPolygon'
    features = []

    regions_lines = sct_dictionary[1]['regions'].splitlines()
    regions_lines = filter(lambda x: x.strip(), regions_lines)  # stolen lambda to remove empty lines
    for line in regions_lines:
        if 'REGIONNAME' in line:
            note = line.split()
            note = (' '.join(note))
        else:
            '''when color is on line, it is the first vertex of polygon'''
            if 'COLOR' in line:
                '''check if polygon already exists, if it does, add first waypoint to end (according to geojson spec)'''
                if polygon is not None:
                    polygon.append(start_vertex)
                    '''print out list of vertexes (polygon)'''
                    feature_id += 1
                    json_output = returningeojson([[polygon]], feature_id, note, color, feature_type)
                    features.append(json_output)

                '''if polygon doesn't yet exist, pass and start looking for first vertex'''

                '''split line into list items'''
                temp_split = line.split()

                '''select list items for lat/lon, name them as variables & turn lists into strings'''
                lat = ",".join(temp_split[1:2])
                lon = ",".join(temp_split[2:3])
                color = ",".join(temp_split[0:1])
                '''print created vars'''
                # print(color,",", note)
                start_vertex = [dms2dec_func(lon), dms2dec_func(lat)]
                polygon = [start_vertex]

            else:
                '''when there is no color, the vertex belongs to last poly that was started with color.'''

                '''count vertex'''
                other_vertex_count += 1

                '''split line into list items'''
                temp_split = line.split()
                # print(temp_split)  # ['N053.26.59.325', 'E005.41.06.579']
                '''select list items for lat/lon and name them as variables & turn lists into strings'''
                lat = ",".join(temp_split[0:1])
                lon = ",".join(temp_split[1:2])
                # print(lat, lon)  # N053.26.59.325 E005.41.06.579
                '''print created vars'''
                vertex = [dms2dec_func(lon), dms2dec_func(lat)]
                # print(vertex)  # [4.8268627777777775, 53.11607277777778]
                polygon.append(vertex)

    features = [feature_id, features, 'importregion-out/regions']
    return features


def artcc_p(sct_dictionary):  # parser for the [ARTCC LOW] Section
    feature_id = sct_dictionary[0]
    features = []
    multi_lines = None
    feature_type = 'MultiLineString'
    artcc_lines = sct_dictionary[1]['artcc_low'].splitlines()
    artcc_lines = filter(lambda x: x.strip(), artcc_lines)  # stolen lambda to remove empty lines
    white_space = '                                         '
    color = 'undef'
    for line in artcc_lines:
        if white_space in line:  # normal item
            coords = line.strip().split()
            lat1 = ",".join(coords[0:1])
            lon1 = ",".join(coords[1:2])
            lat2 = ",".join(coords[2:3])
            lon2 = ",".join(coords[3:4])
            vertex1 = [dms2dec_func(lon1), dms2dec_func(lat1)]
            vertex2 = [dms2dec_func(lon2), dms2dec_func(lat2)]
            edge = [vertex1, vertex2]
            # print(edge)  # [[4.149104722222223, 51.51199361111111], [4.168978611111111, 51.531660555555554]]
            multi_lines.append(edge)
            feature_id += 1

        else:
            if multi_lines is not None:  # first item in multilinestring including title.
                jsonoutput = returningeojson(multi_lines, feature_id, note, color, feature_type)
                features.append(jsonoutput)

            temp_split = line.split('  ')
            temp_split = [temp_split[0].strip(), temp_split[-1].strip()]
            note = temp_split[0]
            coords = temp_split[1].split()
            lat1 = ",".join(coords[0:1])
            lon1 = ",".join(coords[1:2])
            lat2 = ",".join(coords[2:3])
            lon2 = ",".join(coords[3:4])
            vertex1 = [dms2dec_func(lon1), dms2dec_func(lat1)]
            vertex2 = [dms2dec_func(lon2), dms2dec_func(lat2)]
            edge = [vertex1, vertex2]
            # print(edge)  # [[4.149104722222223, 51.51199361111111], [4.168978611111111, 51.531660555555554]]
            multi_lines = [edge]
            feature_id += 1

    features = [feature_id, features, 'importregion-out/artcc_low']
    return features


def geo_p(sct_dictionary):  # parser for the [GEO] Section
    feature_id = sct_dictionary[0]
    features = []
    multi_lines = None
    color_first = None
    color_next = None
    color = None
    note = None
    feature_type = 'MultiLineString'
    geo_lines = sct_dictionary[1]['geo'].splitlines()
    geo_lines = filter(lambda x: x.strip(), geo_lines)  # stolen lambda to remove empty lines
    white_space = '                                         '
    for line in geo_lines:
        coords = line.strip().split()
        color_next = ",".join(coords[4:5])
        if color_first is not None:
            if color_first != color_next:
                print(['color_first != color_next:', note, line, color_first, color_next])
                jsonoutput = returningeojson(multi_lines, feature_id, note, color, feature_type)
                # print(note, 'color_first != color_next', color)
                features.append(jsonoutput)
                color_first = color_next
                multi_lines = []
        if white_space in line:  # normal item
            coords = line.strip().split()
            lat1 = ",".join(coords[0:1])
            lon1 = ",".join(coords[1:2])
            lat2 = ",".join(coords[2:3])
            lon2 = ",".join(coords[3:4])
            color = ",".join(coords[4:5])
            vertex1 = [dms2dec_func(lon1), dms2dec_func(lat1)]
            vertex2 = [dms2dec_func(lon2), dms2dec_func(lat2)]
            edge = [vertex1, vertex2]
            multi_lines.append(edge)
            feature_id += 1

        else:  # first item in multilinestring including title.
            temp_split = line.split('  ')
            temp_split = [temp_split[0].strip(), temp_split[-1].strip()]
            note = temp_split[0]
            coords = temp_split[1].split()
            lat1 = ",".join(coords[0:1])
            lon1 = ",".join(coords[1:2])
            lat2 = ",".join(coords[2:3])
            lon2 = ",".join(coords[3:4])
            color = ",".join(coords[4:5])
            color_first = color
            vertex1 = [dms2dec_func(lon1), dms2dec_func(lat1)]
            vertex2 = [dms2dec_func(lon2), dms2dec_func(lat2)]
            edge = [vertex1, vertex2]
            multi_lines = [edge]
            feature_id += 1
            print([note, line, color_first, color_next])

    print('que')
    print(['final polygon', note, color_first, color_next])
    jsonoutput = returningeojson(multi_lines, feature_id, note, color, feature_type)
    features.append(jsonoutput)

    features = [feature_id, features, 'importregion-out/geo']
    return features


def labels_p(sct_dictionary):
    features = []
    feature_type = 'Point'
    feature_id = sct_dictionary[0]
    labels_lines = sct_dictionary[1]['labels'].splitlines()
    section = None
    for line in labels_lines:
        if ';=' in line:
            header_line = line
            header_line = header_line.replace(';', '')
            header_line = header_line.replace('=', '')
            header_line = header_line.replace('~', '')
            header_line = header_line.replace(';', '')
            header_line = header_line.replace(' ', '')
            section = header_line
        else:
            if line:
                feature_id += 1
                coords = line.split('\"')
                coords = [i for i in coords if i]

                text = coords[0]

                coords = coords[1].strip().split()
                lat = coords[0]
                lon = coords[1]
                color = coords[2]
                # print(section, text, lat, lon, color)
                vertex = [dms2dec_func(lon), dms2dec_func(lat)]
                note = section
                text_label = text
                jsonoutput = returningeojson(vertex, feature_id, note, color, feature_type, text_label)
                features.append(jsonoutput)
    features = [feature_id, features, 'importregion-out/labels']
    return features


def returningeojson(polylist, poly_id, note, color, feature_type, text_label = ""):
    # print('-----------------------------------new version ----------------------------------')
    # print(polylist)


    """init dicts"""
    geometry = {}
    feature_item = {}
    ident = {}

    '''add to 2nested lists'''
    inputlist = polylist

    '''add items to dictionary'''
    geometry['type'] = feature_type  # 'MultiPolygon'
    geometry['coordinates'] = inputlist

    feature_item['type'] = 'Feature'

    ident['id'] = poly_id
    ident['name'] = note
    ident['color'] = color
    ident['text_label'] = text_label

    feature_item['properties'] = ident
    feature_item['geometry'] = geometry

    '''send formatted dictionary back'''
    return feature_item


def sct_splitter(data):
    """function to split SCT into dictionary with multiple sections for easy parsing"""
    types = [['[INFO]', 'header'], ['[VOR]', 'info'], ['[NDB]', 'vor'], ['[FIXES]', 'ndb'], ['[AIRPORT]', 'fixes'],
             ['[RUNWAY]', 'airport'], ['[SID]', 'runway'], ['[STAR]', 'sid'], ['[ARTCC HIGH]', 'star'],
             ['[ARTCC]', 'artcc_high'], ['[ARTCC LOW]', 'artcc'], ['[GEO]', 'artcc_low'], ['[REGIONS]', 'geo'],
             ['[LABELS]', 'regions'], ['[HIGH AIRWAY]', 'labels'], ['[LOW AIRWAY]', 'high_airway']]
    sct_split_list = []
    sct_dict = {}
    for item in types:
        sct_delim = item[0]
        sct_name = item[1]

        if sct_delim == '[INFO]':
            sct_split_list = data.split(sct_delim)
            sct_dict[sct_name] = sct_split_list[0]

        elif sct_delim == '[LOW AIRWAY]':
            sct_dict[sct_name] = sct_split_list[1]

        else:
            sct_split_list = sct_split_list[1].split(sct_delim)
            sct_dict[sct_name] = sct_split_list[0]

    return sct_dict
