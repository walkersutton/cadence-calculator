# created by walker
# https://walkercsutton.com
# @walkercsutton

import os
from lxml import etree

DEBUG = True

# TODO
# create cadence element with an ACCURATE cadence
def generateCadenceElement(lat, lon):
	cadence_element = etree.Element("cadence")
	cadence_element.text = str(69)
	return cadence_element

def main():
	
	if DEBUG:
		gpx_filename = "../../../Desktop/ev_ride_min.gpx"
		# gpx_filename = "../../../Desktop/Lunch_Ride_Min.gpx"
	else:
		gpx_filename = input("Enter path of GPX filename: ") 
	
	gpx_filename_fullpath = os.path.abspath(os.path.join('data', gpx_filename))
	
	tree = etree.parse(gpx_filename_fullpath)
	root = tree.getroot()

	# stores all unique element tags up to the 2nd trkpt
	element_set = set()

	# keep track of the number of times iterated over a trkpt element
	trkpt_count = 0

	for element in tree.iter():
		if trkpt_count != 2:
			element_set.add(element.tag)
			if (element.tag == "{http://www.topografix.com/GPX/1/1}trkpt"):
				trkpt_count += 1
		else:
			break

	EXTENSIONS = "{http://www.topografix.com/GPX/1/1}extensions" in element_set
	
	if EXTENSIONS:
		for element in tree.iter():
			if (element.tag == "{http://www.topografix.com/GPX/1/1}trkpt"):
				# print("lat: " + element.attrib["lat"])
				# print("lon: " + element.attrib["lon"])
				# print("trkpt")
				lat = element.attrib["lat"]
				lon = element.attrib["lon"]
			if (element.tag == "{http://www.topografix.com/GPX/1/1}extensions"):
				print("extension")
				element.append(generateCadenceElement(lat, lon))
	else:
		for element in tree.iter():
			if (element.tag == "{http://www.topografix.com/GPX/1/1}trkpt"):
				lat = element.attrib["lat"]
				lon = element.attrib["lon"]
				extensions_element = etree.Element("extensions")
				element.append(extensions_element)
				extensions_element.append(generateCadenceElement(lat, lon))
			
	tree.write('test_file.xml')

	if not DEBUG:
		print("Successfully created a GPX file with cadence")
		# print("The new filename is " + os.path.basename(gpx_filename_fullpath)[:-4] + "_with_cadence.gpx")
		# print("The file is in the directory with main.py")
	
# execute
main()