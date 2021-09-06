def generateCadenceElement(cadence):
	""" Generates a new Element cadence object with the given cadence as its value

	Args:
		cadence::[str]
			The cadence value in RPM to be assigned to the generated object
	
	Returns
		cadence_element::lxml.etree._Element
			A new cadence Element with the specified cadence value
 
	"""
	cadence_element = etree.Element("cadence")
	cadence_element.text = cadence
	return cadence_element