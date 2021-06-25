import unittest
import sys
# sys.path.insert(1, '../calculator')

from haversine import Unit
from calculator import cadence, distance, speed, TIMEUNIT


class TestCalculator(unittest.TestCase):
	def setUp(self):
		self.cog = 16
		self.chainring = 48
		self.tire_width = 25
		self.wheel_diameter = 622

	def testDistance(self):
		boston = (42.3601, -71.0589)
		new_york = (40.7128, -74.0060)

		boston_to_new_york = 306108

		self.assertEqual(boston_to_new_york, int(distance(boston, new_york, dist_unit=Unit.METERS)))
		self.assertEqual(boston_to_new_york, int(distance(new_york, boston, dist_unit=Unit.METERS)))
		self.assertEqual(0, distance(boston, boston, dist_unit=Unit.METERS))
	
	def testCadence(self):
		timestep_0 = (40.685516, -73.931366)
		timestep_1 = (40.685524, -73.931297)
		
		actual_cadence = cadence(timestep_0, timestep_1, self.cog, self.chainring, self.tire_width, self.wheel_diameter, dist_unit=Unit.METERS, time_rate=TIMEUNIT.MINUTE)
		self.assertEqual(55, actual_cadence)

	def testSpeed(self):
		timestep_0 = (40.685516, -73.931366)
		timestep_1 = (40.685524, -73.931297)
		meter_minute_speed = speed(timestep_0, timestep_1, dist_unit=Unit.METERS, time_rate=TIMEUNIT.MINUTE)
		meter_hour_speed = speed(timestep_0, timestep_1, dist_unit=Unit.METERS, time_rate=TIMEUNIT.HOUR)
		mile_hour_speed = speed(timestep_0, timestep_1, dist_unit=Unit.MILES, time_rate=TIMEUNIT.HOUR)
		self.assertEqual(353, meter_minute_speed)
		self.assertEqual(21188, meter_hour_speed)
		self.assertEqual(13, mile_hour_speed)
		

if __name__ == '__main__':
    unittest.main()
