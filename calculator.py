import os
import sys
from lxml import etree
from collections import deque
from statistics import mean
import math

from calculator import generateCadence, generateMPH
from utils import applicableElements
from tester import havList

DEBUG = True

def main():
	gpx_filename = sys.argv[1]
	
	# gpx_filename_fullpath = os.path.abspath(os.path.join('data', gpx_filename))
	gpx_filename_fullpath = os.path.abspath(gpx_filename)
	
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
		exit("One or more of your submitted values is invalid. Try again.")

	tree = etree.parse(gpx_filename_fullpath)
	root = tree.getroot()
	elements = applicableElements(tree)

	distances = havList(tree)
	distances.sort()
	max_cutoff = distances[int(len(distances) * .96)] * 60 / (math.pi * (wheel_diameter + (2 * tire_width)) * (chainring / cog)) 

	if (distances[int(len(distances) * .96)] > 25000):
		exit("you got some SHIT GPS - fuck off")

	last_lon = 0.0
	last_lat = 0.0

	time = 0

	cadences = []
	seconds = []
	speeds = []
	window = deque([0,0,0], maxlen=3)
	delta = int(sys.argv[2]) # 100 # larger value, less smooth - min val is 0
	smoothie = float(sys.argv[3]) # .0 # smaller value, less smooth - max val is 1
	print("max cutoff: "  + str(max_cutoff))

	# if the gpx file already contains `extensions` elements
	if elements['extensions'] != '':
		for element in tree.iter():
			seconds.append(time)
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
			if (element.tag == elements['extensions']):
				cadence = float(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				m = mean(window)
				if m > 120:
					print("the mean is: " + str(m))
				if cadence > max_cutoff:
					print('cadence is over the max cutoff')
					cadence = m
					print("particularly large cadence: " + str(cadence))
					print("current mean: " + str(m))
				elif (cadence > m + delta and cadence < m - delta):
					print('correcting bad value: ' + str(cadence) + "to this better value: " + str(m))
					cadence = m
				else:
					if (cadence > m):
						cadence -= (abs(m - cadence) * smoothie)
					else:
						cadence += (abs(m - cadence) * smoothie)
				cadences.append(cadence)
				window.append(cadence)
				element.append(generateCadenceElement(str(cadence)))
				# print(window)
				last_lat = lat
				last_lon = lon
			time += 1

	# if the gpx file doesn't contain `extensions` elements
	else:
		for element in tree.iter():
			seconds.append(time)
			if (element.tag == elements['trkpt']):
				lat = float(element.attrib["lat"])
				lon = float(element.attrib["lon"])
				extensions_element = etree.Element("extensions")
				cadence = int(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
				m = mean(window)
				if (cadence > m + delta and cadence < m - delta):
					print('correcting bad value: ' + str(cadence) + "to this better value: " + str(m))
					cadence = m
				else:
					if (cadence > m):
						cadence = cadence - (abs(m - cadence) * smoothie)
					else:
						cadence = cadence + (abs(m - cadence) * smoothie)
				cadences.append(cadence)
				window.append(cadence)
				element.append(generateCadenceElement(str(cadence)))
				extensions_element.append(generateCadenceElement((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))

				last_lat = lat
				last_lon = lon
			time += 1


	# cleanup
	new_filename = os.path.basename(gpx_filename_fullpath)[:-4] + "_with_cadence.gpx"
	tree.write(new_filename)

	import plotly.graph_objects as go

	fig = go.Figure()
	fig.add_trace(go.Scatter(x=seconds, y=cadences, name='cadence', line=dict(color='firebrick', width=2)))
	fig.update_layout(title=str('cadence: ' + str(gpx_filename) + " delta: " + str(delta) + " smoothie: " + str(smoothie)),
										xaxis_title='seconds',
										yaxis_title='RPM')
	fig.show()

	# import numpy as np	
	# dists = dists[int(len(dists) * 0): int(len(dists) * .96)]
	# fig = go.Figure(data=go.Histogram(x=dists, histnorm='probability'))
	# fig.update_layout(title=gpx_filename)
	# fig.show()


	# TODO remove once data is smoothed	

	if not DEBUG:
		print("Successfully created a GPX file with cadence")
		print("The new filename is: " + new_filename)
		print("The file is in the directory with main.py")
	
# execute
main()
