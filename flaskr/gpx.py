""" gpx.py """
import json
from lxml import etree

def generateCadenceElement(cadence):
    """ Generates a new Element cadence object with the given cadence as its value

    Args:
                    cadence::[str]
                                    The cadence value in RPM to be assigned to the generated object

    Returns
                    cadence_element::lxml.etree._Element
                                    A new cadence Element with the specified cadence value

    """
    #     cadence_element = etree.Element("cadence")
    #     cadence_element.text = cadence
    #     return cadence_element
    return cadence


def create_gpx(stream):
    """ Creates a GPX file with this stream's data

            Args:
                            stream (obj)

            TODO

            Returns a filename to the newly created gpx file
            TODO tar compress before creating post request
    """
    f = open("st.json")
    stream = json.load(f)

    gpx = etree.Element('gpx', creator='cadecalc.app', xmlns='TODO', version='1.1')
    doc = etree.ElementTree(gpx)
    metadata = etree.SubElement(gpx, 'metadata')
    time = etree.SubElement(metadata, 'time')
    time.text = '2021-07-04T21:22:57Z'
    trk = etree.SubElement(gpx, 'trk')
    name = etree.SubElement(trk, 'name')
    name.text = 'NBD: first ride on the Canyon!'
    type = etree.SubElement(trk, 'type')
    type.text = '1'
    trkseg = etree.SubElement(trk, 'trkseg')
    for ii in range(stream['latlng']['original_size']):
        lat, lon = str(stream['latlng']['data'][ii][0]), str(stream['latlng']['data'][ii][1])
        ele = str(stream['altitude']['data'][ii])
        time = str(stream['time']['data'][ii])
        # cadence = str(stream['cadence']['data'][ii])
        trkpt = etree.SubElement(trkseg, 'trkpt', lat=lat, lon=lon)
        ele_ele = etree.SubElement(trkpt, 'ele')
        ele_ele.text = ele
        # TODO Fix time
        time_ele = etree.SubElement(trkpt, 'time')
        # time.text = '2021-07-04T21:22:57Z'
        time_ele.text = time
        extensions = etree.SubElement(trkpt, 'extensions')
        # invalid tag name with the colon below - use a xmlns or something 
        trackpoint_extension = etree.SubElement(extensions, 'gpxtpxTrackPointExtension')
        heartrate = etree.SubElement(trackpoint_extension, 'gpxtpxhr')
        heartrate.text = '99'
    
    # trk = etree.SubElement(gpx, 'trk', nsmap={'xmlns': 'hello'})
    # trk = etree.SubElement(gpx, 'Country', 
    #                                     name='Germany',
    #                                     Code='DE',
    #                                     Storage='Basic')
    doc.write('output5.xml', xml_declaration=True, encoding='UTF-8') 

    # NSMAP = {
    # 'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
    # None: 'http://www.topografix.com/GPX/1/1',
    # 'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
    # 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    # }


    # schemaLocation = "http://www.topografix.com/GPX/1/1"
    # schemaLocation += "http://www.topografix.com/GPX/1/1/gpx.xsd"
    # schemaLocation += "http://www.garmin.com/xmlschemas/GpxExtensions/v3"
    # schemaLocation += "http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd"
    # schemaLocation += "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    # schemaLocation += "http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"
    # schemaLocation += "http://www.garmin.com/xmlschemas/GpxExtensions/v3"
    # schemaLocation += "http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd"
    # schemaLocation += "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    # schemaLocation += "http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"
    # f = open("test.gpx", "w")
    # gpx = etree.Element('gpx', nsmap=NSMAP)
    # gpx.set('creator', 'Cadence Calculator')
    # gpx.set('version', '1.1')
    # gpx.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
    #     schemaLocation)
    # et = etree.ElementTree(gpx)
    # et = tostring(et, 'unicode')
    # et.write(f)
    # f.close()

    # gpx = gpxpy.gpx.GPX()
    # gpx_track = gpxpy.gpx.GPXTrack()
    # gpx.tracks.append(gpx_track)
    # gpx_segment = gpxpy.gpx.GPXTrackSegment()
    # gpx_track.segments.append(gpx_segment)
    # for ii in range(3):f
    #     gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(ii, 5, elevation=12))
    # with open("output.gpx", "w") as f:
        # f.write( gpx.to_xml())

    
    return stream


# NOTES
# * look into python gpx validation (or maybe just xml)
#   * this was reccomended somewhere https://xerces.apache.org/xerces-c/
# * Library for creating GPX easily
#   * https://github.com/tkrajina/gpxpy
#   * https://pypi.org/project/gpxpy/
#   * https://github.com/kosmo/gpx-from-strava
# * https://www.topografix.com/gpx.asp
# * https://stackoverflow.com/questions/68457696/strava-api-to-export-gpx-file-of-activity
