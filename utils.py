# created by walker
# https://walkercsutton.com
# @walkercsutton

from lxml import etree

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

def applicableElements(tree):
	trkpt_count = 0
	trkpt = ''
	extensions = ''
	cadences = set()

	for element in tree.iter():
		if trkpt_count != 2:
			if ("trkpt" in element.tag):
				trkpt = element.tag
				trkpt_count += 1
			if ("cadence" in element.tag):
				cadences.add(element.tag)
			if ("extensions" in element.tag):
				contains_extensions = True
				extensions = element.tag
		else:
			break
	
	return {
		'trkpt': trkpt,
		'extensions': extensions,
		'cadences': cadences
	}