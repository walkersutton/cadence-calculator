import os
import sys
from lxml import etree
import plotly.graph_objects as go
from collections import deque
from statistics import mean
import math

from calculator import generateCadence, generateSpeed, generateDistance
from utils import applicableElements

DEBUG = True

def actualCadenceList(tree):
	elements = applicableElements(tree)
	cadences = []

	for element in tree.iter():
		if (element.tag in elements['cadences']):
			cadences.append(float(element.text))
				
	return cadences

def derivedCadenceList(tree, cog, chainring, tire_width, wheel_diameter):
	elements = applicableElements(tree)
	derived_cadence = []
	last_lon = 0.0
	last_lat = 0.0
	window = deque([0,0,0], maxlen=8)
	delta = 25
	smoothie = .6

	distances = havList(tree)
	distances.sort()
	max_cutoff = distances[int(len(distances) * .96)] * 60 / (math.pi * (wheel_diameter + (2 * tire_width)) * (chainring / cog)) 

	# if the gpx file already contains `extensions` elements
	if elements['extensions'] != '':
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
			if (element.tag == elements['extensions']):
				cadence = float(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				m = mean(window)
				if (cadence > max_cutoff):
					cadence = 0
					# cadence = m
				elif (cadence > m + delta and cadence < m - delta):
					print('correcting bad value: ' + str(cadence) + "to this better value: " + str(m))
					cadence = m
				else:
					if (cadence > m):
						cadence -= (abs(m - cadence) * smoothie)
					else:
						cadence +=(abs(m - cadence) * smoothie)
				derived_cadence.append(cadence)

				window.append(cadence)
				last_lat = lat
				last_lon = lon
	# if the gpx file doesn't contain `extensions` elements
	else:
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
				cadence = generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter)
				m = mean(window)
				if (cadence > m + delta and cadence < m - delta):
					cadence = m
					derived_cadence.append(cadence)
				else:
					if (cadence > m):
						cadence = cadence - (abs(m - cadence) * smoothie)
					else:
						cadence = cadence + (abs(m - cadence) * smoothie)
				derived_cadence.append(cadence)
				window.append(cadence)
				# if (cadence > (m * (1 - delta)) or cadence < (m * (1 + delta))):
				# 	derived_cadence.append(cadence)
				# 	window.append(cadence)
				last_lat = lat
				last_lon = lon

	return derived_cadence

# TODO remove once data is smoothed
def havList(tree):
	elements = applicableElements(tree)
	distances = []
	last_lon = 0.0
	last_lat = 0.0

	# if the gpx file already contains `extensions` elements
	if elements['extensions'] != '':
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
			if (element.tag == elements['extensions']):
				distances.append(float(generateDistance((last_lat, last_lon), (lat, lon))))
				last_lat = lat
				last_lon = lon
	# if the gpx file doesn't contain `extensions` elements
	else:
		for element in tree.iter():
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
				distances.append(float(generateDistance((last_lat, last_lon), (lat, lon))))
				last_lat = lat
				last_lon = lon

	return distances

def main():
	gpx_filename = sys.argv[1]
	gpx_filename_fullpath = os.path.abspath(gpx_filename)
	tree = etree.parse(gpx_filename_fullpath)

	cog = -1
	chainring = -1
	tire_width = -1
	wheel_diameter = -1
	
	if DEBUG: 
		cog = 14
		chainring = 49
		# cog = 16
		# chainring = 48
		tire_width = 25
		wheel_diameter = 622
	else:
		cog = input("# of teeth on cog: ")
		chainring = input("# of teeth on chainring: ")
		tire_width = input("Tire width (in mm): ")
		wheel_diameter = input("Wheel diameter (in mm): ")
	
	if (cog < 0 or chainring < 0 or tire_width < 0 or wheel_diameter < 0):
		exit("At least one of your submitted values is invalid. Try again.")

	actual_cadence = actualCadenceList(tree)
	derived_cadence = derivedCadenceList(tree, cog, chainring, tire_width, wheel_diameter)
	# speeds = speedList(tree)
	seconds = []


	for ii in range (0, len(derived_cadence)):
		seconds.append(ii)
	c = 0
	# print("avg len: " + str(len(avg_cadence)))
	# print("der len: " + str(len(derived_cadence)))
	# print("sec len: " + str(len(seconds)))
	# for i in seconds:
	# 	avg = avg_cadence[i - 1]
	# 	der = derived_cadence[i - 2]
	# 	if (abs(avg - der) > 10 and der != 0):
	# 		# print("sec: " + str(i - 1) + "        avg: " + str(avg) + "      der: " + str(der))
	# 		c += 1

	# print("count: " + str(c))
	fig = go.Figure()
	
	fig.add_trace(go.Scatter(x=seconds, y=actual_cadence, name='actual cadence', line=dict(color='firebrick', width=2)))

	fig.add_trace(go.Scatter(x=seconds, y=derived_cadence, name = 'derived cadence', line=dict(color='royalblue', width=4)))
	# TODO remove once data is smoothed
	
	
	fig.update_layout(title=str('actual cadence vs derived cadence'),
										xaxis_title='seconds',
										yaxis_title='cadence (RPM)')
	fig.show()
	
# execute
main()
