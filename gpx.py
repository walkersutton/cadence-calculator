def generateCadenceElement(cadence):
    """ Generates a new Element cadence object with the given cadence as its value

    Args:
            cadence::[str]
                    The cadence value in RPM to be assigned to the generated object

    Returns
            cadence_element::lxml.etree._Element
                    A new cadence Element with the specified cadence value

    """
    cadence_element = etree.Element("cadence")
    cadence_element.text = cadence
    return cadence_element


def create_gpx(stream):
    """ Creates a GPX file with this stream's data

            Args:
                    stream (obj)

            TODO

            Returns a filename to the newly created gpx file
            TODO tar compress before creating post request
    """


"""
NOTES
* look into python gpx validation (or maybe just xml)
  * this was reccomended somewhere https://xerces.apache.org/xerces-c/
* Library for creating GPX easily
  * https://github.com/tkrajina/gpxpy
  * https://pypi.org/project/gpxpy/
  * https://github.com/kosmo/gpx-from-strava
* https://www.topografix.com/gpx.asp
* https://stackoverflow.com/questions/68457696/strava-api-to-export-gpx-file-of-activity

"""
