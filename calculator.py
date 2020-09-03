# created by walker
# https://walkercsutton.com
# @walkercsutton

from haversine import haversine, Unit
from lxml import etree
import math

def generateCadence(posn1, posn2, cog, chainring, tire_width, wheel_diameter):
	if (posn1 == (0.0, 0.0)):
		cadence = 0
	else :
		# coordinates are measured in 1 second intervals
		# convert into mm (because I measure tire width in mm)
		# TODO support other systems of measurement
		distance = haversine(posn1, posn2, unit=Unit.METERS) * 1000 
		speed = distance * 60 # speed should be recorded in units/minute since we want cadence measured in RPM, not RPS
		# TODO smooth out bad data
		# if (speed > 1690000):
		# if (speed > 1500000):
		# 	speed = 0
		cadence = speed / (math.pi * (wheel_diameter + (2 * tire_width)) * (chainring / cog))

	return str(int(cadence))

def generateCadenceElement(posn1, posn2, cog, chainring, tire_width, wheel_diameter):	
	cadence = generateCadence(posn1, posn2, cog, chainring, tire_width, wheel_diameter)
	cadence_element = etree.Element("cadence")
	cadence_element.text = cadence

	return cadence_element

# TODO remove once data is smoothed
def generateSpeed(posn1, posn2):
	if (posn1 == (0.0, 0.0)):
		speed = 0
	else :
		# coordinates are measured in 1 second intervals
		distance = haversine(posn1, posn2, unit=Unit.MILES)
		speed = distance * 60 * 60
		if (speed > 60):
			speed = 0
			
	return str(int(speed))