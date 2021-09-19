""" gpx.py """
from datetime import datetime, timedelta
import json
from lxml import etree

def create_gpx(stream: dict, activity: dict) -> str:
    """ Creates a GPX file with this stream's data

            Args:
                stream (obj)

            TODO

            Returns a filename to the newly created gpx file
            TODO tar compress before creating post request
    """
    datetime_fmt = '%Y-%m-%dT%H:%M:%SZ'
    start_datetime = activity['start_time']
    NSMAP = {
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
        'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'
    }
    schema_location = ''
    schema = ['http://www.topografix.com/GPX/1/1 ', 'http://www.topografix.com/GPX/1/1/gpx.xsd ',
    'http://www.garmin.com/xmlschemas/GpxExtensions/v3 ', 'http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd ',
    'http://www.garmin.com/xmlschemas/TrackPointExtension/v1 ', 'http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd']
    for s in schema:
        schema_location += s

    f = open('st.json')
    stream = json.load(f)

    gpx = etree.Element('gpx', creator=activity['device_name'], xmlns='http://www.topografix.com/GPX/1/1', version='1.1', nsmap=NSMAP)
    gpx.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', schema_location)

    doc = etree.ElementTree(gpx)

    metadata = etree.SubElement(gpx, 'metadata')

    time = etree.SubElement(metadata, 'time')
    time.text = start_datetime

    trk = etree.SubElement(gpx, 'trk')

    name = etree.SubElement(trk, 'name')
    name.text = activity['name']

    type = etree.SubElement(trk, 'type')
    type.text = '1'
    # TODO investigate this

    trkseg = etree.SubElement(trk, 'trkseg')

    start_datetime = datetime.strptime(start_datetime, datetime_fmt)
    for ii in range(stream['latlng']['original_size']):
        # we are assuminmg that all streams will have latlng based on the range parameter
        trkpt = etree.SubElement(trkseg, 'trkpt', lat=str(stream['latlng']['data'][ii][0]), lon=str(stream['latlng']['data'][ii][1]))

        if 'altitude' in stream:
            ele = etree.SubElement(trkpt, 'ele')
            ele.text = str(stream['a`ltitude']['data'][ii])

        time = etree.SubElement(trkpt, 'time')
        time.text = (start_datetime + timedelta(seconds=int(stream['time']['data'][ii]))).strftime('%Y-%m-%dT%H:%M:%SZ')

        extensions = etree.SubElement(trkpt, 'extensions')
        # invalid tag name with the colon below - use a xmlns or something
        trackpoint_extension = etree.SubElement(extensions, 'TrackPointExtension')
        # extension_types = ['heartrate', 'cadence', 'latlng', 'distance', ]
        # TODO
        # maybe make a for loop here? depending on where the elements go - i imagine they don't all belong to TrackpointExtension
        if 'heartrate' in stream:
            heartrate = etree.SubElement(trackpoint_extension, 'hr')
            heartrate.text = str(stream['heartrate']['data'][ii])
        # if 'cadence' in stream:
        #     cadence = etree.SubElement(trackpoint_extension, 'cadence')
        #     cadence.text = str(stream['cadence']['data'][ii])
        # if 'watts' in stream:
        #     watts = etree.SubElement(trackpoint_extension, 'watts')
        #     watts.text = str(stream['watts']['data'][ii])
        # if 'temp' in stream:
        #     temp = etree.SubElement(trackpoint_extension, 'temp')
        #     temp.text = str(stream['temp']['data'][ii])
        # if 'moving' in stream:
        #     moving = etree.SubElement(trackpoint_extension, 'moving')
        #     moving.text = str(stream['moving']['data'][ii])
        # if 'velocity_smooth' in stream:
        #     velocity_smooth = etree.SubElement(trackpoint_extension, 'velocity_smooth')
        #     velocity_smooth.text = str(stream['velocity_smooth']['data'][ii])
        # if 'grade_smooth' in stream:
        #     grade_smooth = etree.SubElement(trackpoint_extension, 'grade_smooth')
        #     grade_smooth.text = str(stream['grade_smooth']['data'][ii])
            # OTHER STREAM
            # distance - don't need(?)
            # DistanceStream	An instance of DistanceStream.
    doc.write('output6.xml', xml_declaration=True, encoding='UTF-8', pretty_print=True)

    return 'output6.xml'


# NOTES
# * look into python gpx validation (or maybe just xml)
#   * this was reccomended somewhere https://xerces.apache.org/xerces-c/
# * Library for creating GPX easily
#   * https://github.com/tkrajina/gpxpy
#   * https://pypi.org/project/gpxpy/
#   * https://github.com/kosmo/gpx-from-strava
# * https://www.topografix.com/gpx.asp
# * https://stackoverflow.com/questions/68457696/strava-api-to-export-gpx-file-of-activity
