""" cadence.py """
import logging
from collections import deque
from statistics import mean
import math

# from utils import applicableElements, distance
# from tester import havList

DEBUG = True


def generate_cadence(distance_travelled, chainring, cog, wheel_diameter=622, tire_width=25):
    """ Generates an integer value for the instantaneous cadence

    Args:
            distance_travelled: float
                    The distance travelled in M/s
            chainring: int
                    The chainring size
            cog: int
                    The cog size
            wheel_diameter: int
                    The wheel diameter in mm
            tire_width: int
                    The tire width in mm
    Returns
            The instantaneous cadence as an integer in revolutions per time_rate
    """
    try:
        return distance_travelled * 60 / (math.pi * (wheel_diameter + (2 * tire_width)) / 1000 * (chainring / cog))
    except Exception as e:
        logging.error('error generating instantaneous cadence:')
        logging.error(e)
        return None


# might want tire_width, diameter, etc.
def generate_cadence_data(distances, chainring, cog, wheel_diameter, tire_width):
    """ Generates a list of cadence values based on input
            Args:
                    distances:
                            TODO
                    chainring:
                            TODO
                    cog:
                            TODO
            Returns a list of int
                    representing instantaneous cadence values in rotations per minute
    """
    cadences = []
    last_distance_travelled = 0
    for distance_travelled in distances:
        #  use bike Class?
        cadences.append(generate_cadence(
            distance_travelled - last_distance_travelled, chainring, cog, wheel_diameter, tire_width))
        last_distance_travelled = distance_travelled
    return cadences
    # TODO we might want to clean cadences to smooth over?

# establishing a maxium cadence value
# 	max_cutoff = distances[int(len(distances) * .96)] * 60 / (math.pi * (wheel_diameter + (2 * tire_width)) * (chainring / cog))
# 	if (distances[int(len(distances) * .96)] > 25000):
# 		exit("you got some SHIT GPS - fuck off")

# 	window = deque([0,0,0], maxlen=3)
# 	delta = int(sys.argv[2]) # 100 # larger value, less smooth - min val is 0
# 	smoothie = float(sys.argv[3]) # .0 # smaller value, less smooth - max val is 1
# 	print("max cutoff: "  + str(max_cutoff))

# 	# if the gpx file already contains `extensions` elements
# 	if elements['extensions'] != '':
# 		for element in tree.iter():
# 			seconds.append(time)
# 			if (element.tag == elements['trkpt']):
# 				lat = float(element.attrib["lat"])
# 				lon = float(element.attrib["lon"])
# 			if (element.tag == elements['extensions']):
# 				cadence = float(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
# 				m = mean(window)
# 				if m > 120:
# 					print("the mean is: " + str(m))
# 				if cadence > max_cutoff:
# 					print('cadence is over the max cutoff')
# 					cadence = m
# 					print("particularly large cadence: " + str(cadence))
# 					print("current mean: " + str(m))
# 				elif (cadence > m + delta and cadence < m - delta):
# 					print('correcting bad value: ' + str(cadence) + "to this better value: " + str(m))
# 					cadence = m
# 				else:
# 					if (cadence > m):
# 						cadence -= (abs(m - cadence) * smoothie)
# 					else:
# 						cadence += (abs(m - cadence) * smoothie)
# 				cadences.append(cadence)
# 				window.append(cadence)
# 				element.append(generateCadenceElement(str(cadence)))
# 				# print(window)
# 				last_lat = lat
# 				last_lon = lon
# 			time += 1

# 	# if the gpx file doesn't contain `extensions` elements
# 	else:
# 		for element in tree.iter():
# 			seconds.append(time)
# 			if (element.tag == elements['trkpt']):
# 				lat = float(element.attrib["lat"])
# 				lon = float(element.attrib["lon"])
# 				extensions_element = etree.Element("extensions")
# 				cadence = int(generateCadence((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))
# 				m = mean(window)
# 				if (cadence > m + delta and cadence < m - delta):
# 					print('correcting bad value: ' + str(cadence) + "to this better value: " + str(m))
# 					cadence = m
# 				else:
# 					if (cadence > m):
# 						cadence = cadence - (abs(m - cadence) * smoothie)
# 					else:
# 						cadence = cadence + (abs(m - cadence) * smoothie)
# 				cadences.append(cadence)
# 				window.append(cadence)
# 				element.append(generateCadenceElement(str(cadence)))
# 				extensions_element.append(generateCadenceElement((last_lat, last_lon), (lat, lon), cog, chainring, tire_width, wheel_diameter))

# 				last_lat = lat
# 				last_lon = lon
# 			time += 1


# 	import plotly.graph_objects as go

# 	fig = go.Figure()
# 	fig.add_trace(go.Scatter(x=seconds, y=cadences, name='cadence', line=dict(color='firebrick', width=2)))
# 	fig.update_layout(title=str('cadence: ' + str(gpx_filename) + " delta: " + str(delta) + " smoothie: " + str(smoothie)),
# 										xaxis_title='seconds',
# 										yaxis_title='RPM')
# 	fig.show()

# 	# import numpy as np
# 	# dists = dists[int(len(dists) * 0): int(len(dists) * .96)]
# 	# fig = go.Figure(data=go.Histogram(x=dists, histnorm='probability'))
# 	# fig.update_layout(title=gpx_filename)
# 	# fig.show()
