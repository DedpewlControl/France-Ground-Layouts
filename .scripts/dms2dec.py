def dms2dec_func(dmscoord):

    # inputcoord = 'N052.18.43.297'
    inputcoord = '{}'.format(dmscoord)
    # split coordinate
    inputstring = inputcoord.split('.')

    # convert list to string
    degree = ','.join(inputstring[0:1])
    minute = ','.join(inputstring[1:2])
    second = ','.join(inputstring[2:3])
    fracsec = ','.join(inputstring[3:4])

    # split degree/sign
    if 'S' in degree:
        degree = degree.replace('S', '')
        sign = '-1'
    if 'N' in degree:
        degree = degree.replace('N', '')
        sign = '1'
    if 'W' in degree:
        degree = degree.replace('W', '')
        sign = '-1'
    if 'E' in degree:
        degree = degree.replace('E', '')
        sign = '1'

    # turn strings into floats
    sign = float(sign)
    degree = float(degree)
    minute = float(minute)
    second = float(second)
    fracsec = float(fracsec)
    second = second+(fracsec/1000)

    # combine floats
    decimalout = sign*(degree+(minute/60)+(second/3600))

    # return result to source
    return decimalout


def dec2dms_func(deccoord):

    outputcoord = []
    count0 = 0

    # create signs
    if (deccoord[0]) < 0:
        sign1 = 'W'
    else:
        sign1 = 'E'
    if (deccoord[1]) < 0:
        sign2 = 'S'
    else:
        sign2 = 'N'

    for item in deccoord:
        dd = item
        is_positive = dd >= 0
        dd = abs(dd)
        minutes, seconds = divmod(dd * 3600, 60)
        seconds = round(seconds, 3)
        seconds1, frac_sec = divmod(seconds, 1)
        degrees, minutes = divmod(minutes, 60)
        # degrees = degrees if is_positive else -degrees

        degrees = str(int(degrees))
        degrees = degrees.zfill(3)

        minutes = str(int(minutes))
        minutes = minutes.zfill(2)

        seconds = str(int(seconds))
        seconds = seconds.zfill(2)

        frac_sec = str(round(frac_sec, 3))
        frac_sec = frac_sec.split('.')[1]

        # check if fracsec didn't round correctly
        if len(frac_sec) == 2:
            frac_sec = '{}0'.format(frac_sec)

        if len(frac_sec) == 1:
            frac_sec = '{}00'.format(frac_sec)

        # construct coordinate
        if count0 == 0:
            dmscoord = '{}{}.{}.{}.{}'.format(sign1, degrees, minutes, seconds, frac_sec)
        else:
            dmscoord = '{}{}.{}.{}.{}'.format(sign2, degrees, minutes, seconds, frac_sec)
        count0 += 1
        outputcoord.append(dmscoord)

    return outputcoord
