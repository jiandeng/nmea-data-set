import pynmea2 as nmea
import pandas as pd
import numpy as np
import sys

def nmea_to_dataframe(file):
    f = open(file)
    content = f.readlines()
    f.close()

    sequence = 0
    records = []
    ep = {
        'fixseq':0,
        'fixtime':0,
        'fixtype':np.nan,
        'timestamp':np.nan,
        'latitude':np.nan,
        'longitude':np.nan,
        'altitude':np.nan,
        'ustar':np.nan,
        'vstar':np.nan,
        'pdop':np.nan,
        'hdop':np.nan,
        'vdop':np.nan,
        'speed':np.nan,
        'course':np.nan,
        'tag':'',
    }
    for line in content:
        time = line[:19]
        data = line[25:]
        if data is None or data == '':
            continue
        time = pd.Timestamp(time)
        if data.startswith('===='):
            start_time = time
            sequence += 1
            continue

        d = nmea.parse(data)
        if type(d) == nmea.nmea.ProprietarySentence:
            continue
        if d.sentence_type == 'GGA':
            gga = d
            gsa = None
            gpgsv = None
            glgsv = None
            rmc = None
        elif d.sentence_type == 'GSA':
            if gga is not None:
                gsa = d
        elif d.identifier() == 'GPGSV,':
            if gsa is not None:
                gpgsv = d
        elif d.identifier() == 'GLGSV,':
            if gpgsv is not None:
                glgsv = d
        elif d.sentence_type == 'RMC':
            if glgsv is not None:
                rmc = d

        if rmc is not None:
            point = ep.copy()
            point['fixsequence'] = sequence
            point['fixtime'] = (time - start_time).seconds
            point['timestamp'] = pd.Timestamp(rmc.datetime)
            if rmc.is_valid:
                point['latitude'] = rmc.latitude
                point['longitude'] = rmc.longitude
                point['speed'] = rmc.spd_over_grnd
                point['course'] = rmc.true_course
                point['vstar'] = int(gpgsv.num_sv_in_view) + int(glgsv.num_sv_in_view)
                point['fixtype'] = int(gsa.mode_fix_type)
                point['pdop'] = float(gsa.pdop)
                point['hdop'] = float(gsa.hdop)
                point['vdop'] = float(gsa.vdop)
                point['ustar'] = int(gga.num_sats)
                if gga.altitude is not None:
                    point['height'] = gga.altitude
            records.append(point)
            gga = None
            gsa = None
            gpgsv = None
            glgsv = None
            rmc = None

    df = pd.DataFrame(records)
    return df


if __name__ == '__main__':
    df = nmea_to_dataframe(sys.argv[1])
    print df.tail()


