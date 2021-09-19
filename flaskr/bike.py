""" bike.py """

# TODO
# future improvement
class Bike:
    """ Represents a bike

    Args:
            self.chainring:			the number of teeth on this bike's chainring
            self.cog:				the number of teeth on this bike's cog
            self.tire_width:		the width of this bike's tires
            self.unit:				the units being used to represent tire_width and wheel_diameter
            self.wheel_diameter:	the diameter of this bike's wheels

    """

    def __init__(self, chainring, cog, tire_width, wheel_diameter):
        """ constructor """
        self.chainring = chainring
        self.cog = cog
        self.tire_width = tire_width
        # self.unit = unit
        self.wheel_diameter = wheel_diameter

    def distance_per_revolution(self, unit):
        """ Determines how much distance this bike travels per chainring revolution

        Args:
                unit:

        """

    def method_b(self):
        """ meslkdjf"""
        return self.chainring * self.cog
