""" utils.py """
from enum import Enum
import math
from haversine import haversine, Unit


class TIMEUNIT(Enum):
    """ TIMEUNIT TODO """
    SECOND = 1
    MINUTE = 60
    HOUR = 3600


def distance(orig, dest, dist_unit=Unit.METERS):
    """ Determines the distance between two GPS coordinates

    Args:
            orig: (float, float)
                    The origin GPS coordinate in (lat, lon) format
            dest: (float, float)
                    The destination GPS coordinate in (lat, lon) format
            [dist_unit]: haversine.Unit
                    The unit to be used for length

    Returns a float
            The distance (in dist_units) between the two coordinates
    """
    if orig == (0.0, 0.0):
        computed_distance = 0
    else:
        computed_distance = haversine(orig, dest, dist_unit)

    return computed_distance


def cadence(orig, dest, cog, chainring, tire_width, wheel_diameter, dist_unit=Unit.METERS, time_rate=TIMEUNIT.MINUTE):
    """ Generates an integer value for the instantaneous cadence

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
    """
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
    """ Generates an integer value for the instantaneous speed

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
    """
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


def applicableElements(tree):
    """
        applicableElements(tree)
        - returns necessary information about the tree
            * trkpt: a string representing the tag of a `trkpt` element
            * extensions: a string representing the tag of an `extensions` element
                                        this is also used to determine the existence of `extensions` elements
            * cadences: a set containing all of the string representations of cadences
                                    this is necessary because some gpx files save many cadence instances on the same interval
            - TODO improve return object names
    """
    trkpt_count = 0
    trkpt = ''
    extensions = ''
    cadences = set()

    for element in tree.iter():
        if trkpt_count != 2:
            if "trkpt" in element.tag:
                trkpt = element.tag
                trkpt_count += 1
            if "cadence" in element.tag:
                cadences.add(element.tag)
            if "extensions" in element.tag:
                # contains_extensions = True
                extensions = element.tag
        else:
            break

    return {
        'trkpt': trkpt,
        'extensions': extensions,
        'cadences': cadences
    }
