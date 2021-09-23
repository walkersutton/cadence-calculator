''' utils.py '''
''' TODO merge with cadence.py'''
from enum import Enum
import math
from haversine import haversine, Unit


class TIMEUNIT(Enum):
    ''' TIMEUNIT TODO '''
    SECOND = 1
    MINUTE = 60
    HOUR = 3600


def distance(orig: tuple[float, float], dest: tuple[float, float], dist_unit: Unit.Meters = Unit.METERS) -> float:
    ''' Determines the distance between two GPS coordinates

    Args:
        orig:
    		The origin GPS coordinate in (lat, lon) format
        dest:
        	The destination GPS coordinate in (lat, lon) format
        [dist_unit]:
            The unit to be used for length

    Returns:
        The distance (in dist_units) between the two coordinates
    '''
    if orig == (0.0, 0.0):
        computed_distance = 0
    else:
        computed_distance = haversine(orig, dest, dist_unit)

    return computed_distance


def cadence(orig, dest, cog, chainring, tire_width, wheel_diameter, dist_unit=Unit.METERS, time_rate=TIMEUNIT.MINUTE):
    ''' Generates an integer value for the instantaneous cadence

    Args:
            orig: (float, float)
                    The origin GPS coordinate in (lat, lon) format
            dest: (float, float)
                    The destination GPS coordinate in (lat, lon) format
            cog: int
                    The cog size
            chainring: int
                    The chainring size
            tire_width: int
                    The tire width in milimeters
            wheel_diameter: int
                    The wheel diameter in milimeters
            [dist_unit]: haversine.Unit
                    The unit to be used for length
            [time_rate]: TIMEUNIT
                    The rate at which the speed should be computed, represented as a TIMEUNIT

    Returns
            The instantaneous cadence as an integer in revolutions per time_rate
    '''
    if orig == (0.0, 0.0):
        computed_cadence = 0
    else:
        # coordinates are measured in 1 second intervals
        # convert into mm (because I measure tire width in mm)
        # TODO support other systems of measurement
        MILIMETER_TO_METER = 1000
        computed_speed = speed(
            orig, dest, dist_unit=dist_unit, time_rate=time_rate)
        computed_cadence = computed_speed / \
            (math.pi * ((wheel_diameter + (2 * tire_width)) /
             MILIMETER_TO_METER) * (chainring / cog))

    return int(computed_cadence)


def speed(orig, dest, dist_unit=Unit.METERS, time_rate=TIMEUNIT.HOUR):
    ''' Generates an integer value for the instantaneous speed

    Args:
            orig: (float, float)
                    The origin GPS coordinate in (lat, lon) format
            dest: (float, float)
                    The destination GPS coordinate in (lat, lon) format
            [dist_unit]: haversine.Unit
                    The unit to be used for length
            [time_rate]: TIMEUNIT
                    The rate at which the speed should be computed, represented as a TIMEUNIT

    Returns
            The instantaneous speed as an integer
    '''
    if orig == (0.0, 0.0):
        computed_speed = 0
    else:
        # coordinates are measured in 1 second intervals
        computed_distance = distance(orig, dest, dist_unit)
        computed_speed = computed_distance * time_rate.value
        # TODO this was a check to make sure speed wasn't ridiculous (over 60mph) - do this more sensibly
        # if (computed_speed > 60):
        # 	computed_speed = 0
    return int(computed_speed)