# created by walker
# https://walkercsutton.com
# @walkercsutton

import os
from lxml import etree
import plotly.graph_objects as go

from calculator import generateCadence, generateSpeed
from utils import applicableElements

DEBUG = True

def getAverageCadenceList(tree):
	elements = applicableElements(tree)
	cur_cadences = []
	avg_cadences = []
	cur_index = 0

	for element in tree.iter():
		if (element.tag in elements['cadences']):
			cur_cadences.append(int(element.text))
			if (len(cur_cadences) == len(elements['cadences'])):
				sum = 0
				for cadence in cur_cadences:
					sum += cadence
				avg_cadences.append(sum // len(elements['cadences']))
				cur_cadences = []
				
	return avg_cadences

def getDerivedCadenceList(tree, cog, chainring, tire_width, wheel_diameter):
	elements = applicableElements(tree)
	derived_cadence = []
	last_lon = 0.0
	last_lat = 0.0

	# if the gpx file already contains `extensions` elements
	if elements['extensions'] != '':
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
			if (element.tag == elements['extensions']):
				derived_cadence.append(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				last_lat = lat
				last_lon = lon
	# if the gpx file doesn't contain `extensions` elements
	else:
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
				derived_cadence.append(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				last_lat = lat
				last_lon = lon

	return derived_cadence

# TODO remove once data is smoothed
def getSpeedList(tree):
	elements = applicableElements(tree)
	speeds = []
	last_lon = 0.0
	last_lat = 0.0

	# if the gpx file already contains `extensions` elements
	if elements['extensions'] != '':
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
			if (element.tag == elements['extensions']):
				speeds.append(generateSpeed((last_lat, last_lon), (lat, lon)))
				last_lat = lat
				last_lon = lon
	# if the gpx file doesn't contain `extensions` elements
	else:
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
				speeds.append(generateSpeed((last_lat, last_lon), (lat, lon)))
				last_lat = lat
				last_lon = lon

	return speeds

def main():
	#TODO fix this to only allow files in same directory
	if DEBUG:
		gpx_filename = "../terry_full_orig.gpx"
	else:
		gpx_filename = input("Enter path of GPX filename: ") 

	gpx_filename_fullpath = os.path.abspath(os.path.join('data', gpx_filename))
	tree = etree.parse(gpx_filename_fullpath)

	cog = -1
	chainring = -1
	tire_width = -1
	wheel_diameter = -1
	
	if DEBUG: 
		cog = 14
		chainring = 49
		tire_width = 25
		wheel_diameter = 622
	else:
		cog = input("# of teeth on cog: ")
		chainring = input("# of teeth on chainring: ")
		tire_width = input("Tire width (in mm): ")
		wheel_diameter = input("Wheel diameter (in mm): ")
	
	if (cog < 0 or chainring < 0 or tire_width < 0 or wheel_diameter < 0):
		exit("At least one of your submitted values is invalid. Try again.")

	avg_cadence = getAverageCadenceList(tree)
	derived_cadence = getDerivedCadenceList(tree, cog, chainring, tire_width, wheel_diameter)
	speeds = getSpeedList(tree)
	seconds = []

	for ii in range (0, len(avg_cadence)):
		seconds.append(ii)

	fig = go.Figure()
	fig.add_trace(go.Scatter(x=seconds, y=avg_cadence, name='actual cadence', line=dict(color='firebrick', width=2)))
	fig.add_trace(go.Scatter(x=seconds, y=derived_cadence, name = 'derived cadence', line=dict(color='royalblue', width=2)))
	# TODO remove once data is smoothed
	# fig.add_trace(go.Scatter(x=seconds, y=speeds, name = 'perceived speed', line=dict(color='#AB63FA', width=6)))
	fig.update_layout(title='actual cadence vs derived cadence',
										xaxis_title='seconds',
										yaxis_title='cadence (RPM)')
	fig.show()
	
# execute
main()