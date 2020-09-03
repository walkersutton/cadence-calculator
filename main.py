# created by walker
# https://walkercsutton.com
# @walkercsutton

import os
from lxml import etree

from calculator import generateCadenceElement
from utils import applicableElements

DEBUG = True

def main():
	#TODO fix this to only allow files in same directory
	if DEBUG:
		# gpx_filename = "../../../Desktop/ev_ride_min.gpx"
		# gpx_filename = "../../../Desktop/ev_ride.gpx"
		gpx_filename = "../../../Desktop/strava_full.gpx"
		# gpx_filename = "../../../Desktop/Lunch_Ride_Min.gpx"
	else:
		gpx_filename = input("Enter path of GPX filename: ") 

	gpx_filename_fullpath = os.path.abspath(os.path.join('data', gpx_filename))
	
	cog = -1
	chainring = -1
	tire_width = -1
	wheel_diameter = -1

	if DEBUG: 
		cog = 16
		chainring = 48
		tire_width = 25
		wheel_diameter = 622
	else:
		cog = input("# of teeth on cog: ")
		chainring = input("# of teeth on chainring: ")
		tire_width = input("Tire width (in mm): ")
		wheel_diameter = input("Wheel diameter (in mm): ")
	
	if (cog < 0 or chainring < 0 or tire_width < 0 or wheel_diameter < 0):
		exit("At least one of your submitted values is invalid. Try again.")

	tree = etree.parse(gpx_filename_fullpath)
	root = tree.getroot()
	elements = applicableElements(tree)
	last_lon = 0.0
	last_lat = 0.0

	# if the gpx file already contains `extensions` elements
	if elements['extensions'] != '':
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
			if (element.tag == elements['extensions']):
				element.append(generateCadenceElement((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				last_lat = lat
				last_lon = lon
	# if the gpx file doesn't contain `extensions` elements
	else:
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
				extensions_element = etree.Element("extensions")
				element.append(extensions_element)
				extensions_element.append(generateCadenceElement((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				last_lat = lat
				last_lon = lon

	# cleanup
	new_filename = os.path.basename(gpx_filename_fullpath)[:-4] + "_with_cadence.gpx"
	tree.write(new_filename)

	if not DEBUG:
		print("Successfully created a GPX file with cadence")
		print("The new filename is: " + new_filename)
		print("The file is in the directory with main.py")
	
# execute
main()