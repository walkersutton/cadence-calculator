from datetime import datetime, timedelta
import json
import os
from lxml import etree

# TODO this needs to be broken down into smaller logical parts
def create_gpx(stream: dict, activity: dict, filename: str, filetype: str) -> bool:
    """ Creates a GPX file with this stream's data

    Args:
        stream:
            a Strava stream object with all
            TODO link to stream schema
        activity:
            a Strava activity object
        filename:
            the desired file name
        filetype:
            the desired file type
    Returns:
        Whether or not the file was successfully created
    """
    # activity = {
    #     'start_time': '2021-09-14T10:28:25Z',
    #     'device_name': 'wahooo',
    #     'name': 'mornnning ride'
    # }
    datetime_fmt = '%Y-%m-%dT%H:%M:%SZ'
    start_datetime = activity['start_date']
    XSI = 'http://www.w3.org/2001/XMLSchema-instance'
    GPXTPX = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    GPXX = 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'
    NSMAP = {
        'xsi': XSI,
        'gpxtpx': GPXTPX,
        'gpxx': GPXX
    }
    schema_location = ''
    schema = ['http://www.topografix.com/GPX/1/1 ', 'http://www.topografix.com/GPX/1/1/gpx.xsd ',
    'http://www.garmin.com/xmlschemas/GpxExtensions/v3 ', 'http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd ',
    'http://www.garmin.com/xmlschemas/TrackPointExtension/v1 ', 'http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd']
    for s in schema:
        schema_location += s

    # f = open('st.json')
    # stream = json.load(f)
    creator = 'todo replace creator name'
    gpx = etree.Element('gpx', creator=creator, xmlns='http://www.topografix.com/GPX/1/1', version='1.1', nsmap=NSMAP)
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
    # I thinkkkkk 1==bikeActivity, but I could be wrong

    trkseg = etree.SubElement(trk, 'trkseg')

    start_datetime = datetime.strptime(start_datetime, datetime_fmt)
    for ii in range(stream['latlng']['original_size']):
        # we are assuminmg that all streams will have latlng based on the range parameter
        trkpt = etree.SubElement(trkseg, 'trkpt', lat=str(stream['latlng']['data'][ii][0]), lon=str(stream['latlng']['data'][ii][1]))

        if 'altitude' in stream:
            ele = etree.SubElement(trkpt, 'ele')
            ele.text = str(stream['altitude']['data'][ii])

        time = etree.SubElement(trkpt, 'time')
        time.text = (start_datetime + timedelta(seconds=int(stream['time']['data'][ii]))).strftime('%Y-%m-%dT%H:%M:%SZ')

        extensions = etree.SubElement(trkpt, 'extensions')
        # invalid tag name with the colon below - use a xmlns or something
        trackpoint_extension = etree.SubElement(extensions, '{%s}TrackPointExtension' % (GPXTPX))
        # extension_types = ['heartrate', 'cadence', 'latlng', 'distance', ]
        # TODO
        # maybe make a for loop here? depending on where the elements go - i imagine they don't all belong to TrackpointExtension
        if 'heartrate' in stream:
            heartrate = etree.SubElement(trackpoint_extension, '{%s}hr' % (GPXTPX))
            heartrate.text = str(stream['heartrate']['data'][ii])
        if 'cadence' in stream:
            cadence = etree.SubElement(trackpoint_extension, 'cadence')
            cadence.text = str(stream['cadence']['data'][ii])
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
    # TODO
    # if filetype == 'gpx':
    #     pass
    # elif filetype == 'tar.gz':
    #     pass
    # else:
    #     logging.error('invalid file type')
    #     pass

    filename = f'{filename}.{filetype}'
    doc.write(filename, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    return os.path.exists(filename)

# NOTES
# * look into python gpx validation (or maybe just xml)
#   * this was reccomended somewhere https://xerces.apache.org/xerces-c/
# * Library for creating GPX easily
#   * https://github.com/tkrajina/gpxpy
#   * https://pypi.org/project/gpxpy/
#   * https://github.com/kosmo/gpx-from-strava
# * https://www.topografix.com/gpx.asp
# * https://stackoverflow.com/questions/68457696/strava-api-to-export-gpx-file-of-activity
