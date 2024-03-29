import logging
# from collections import deque
# from statistics import mean
import math

# from utils import applicableElements, distance
# from tester import havList

DEBUG = True


def generate_cadence(distance_travelled: float, chainring: int, cog: int, wheel_diameter: int = 622, tire_width: int = 25) -> float:
    ''' Generates an integer value for the instantaneous cadence

    Args:
        distance_travelled:
                the distance travelled in M/s
        chainring:
                the chainring size
        cog:
                the cog size
        wheel_diameter:
                the wheel diameter in mm
        tire_width
                the tire width in mm
    Returns:
                The instantaneous cadence as an integer in revolutions per minute
    '''
    # TODO - important
    # i think this is chalked - need to look closely at this
    try:
        return distance_travelled * 60 / (math.pi * (wheel_diameter + (2 * tire_width)) / 1000 * (chainring / cog))
    except Exception as e:
        logging.error('error generating instantaneous cadence:')
        logging.error(e)
        return None


def generate_cadence_data(distances: list, chainring: int, cog: int, wheel_diameter: int = 622, tire_width: int = 25):
    # def generate_cadence_data(distances: list, chainring: int, cog: int, wheel_diameter: int = 622, tire_width: int = 25) -> list[int]:
    ''' Generates a list of cadence values based on input

    Args:
        distances:
            distances measured from the origin in 1 second intervals (*usuallly 1 seoncd intervals)
        chainring:
            the chainring size
        cog:
            the cog size
        wheel_diameter:
            the wheel diameter in mm
        tire_width
            the tire width in mm

    Returns:
        The instantaneous cadence values in revolutions per minute
    '''
    try:
        cadences = []
        last_distance_travelled = 0
        for distance_travelled in distances:
            #  use bike Class?
            cadences.append(int(generate_cadence(
                distance_travelled - last_distance_travelled, chainring, cog, wheel_diameter, tire_width)))
            last_distance_travelled = distance_travelled
        return cadences
    except Exception as e:
        logging.error('error generating cadence data:')
        logging.error(e)
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
