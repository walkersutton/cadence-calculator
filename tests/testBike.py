import unittest
import sys
# sys.path.insert(1, '../calculator')

from haversine import Unit
from calculator import cadence, distance, speed, TIMEUNIT


class TestBike(unittest.TestCase):
	def setUp(self):
		self.cog = 16
		self.chainring = 48
		self.tire_width = 25
		self.wheel_diameter = 622


if __name__ == '__main__':
    unittest.main()
