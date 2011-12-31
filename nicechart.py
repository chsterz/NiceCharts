#!/usr/bin/env python

#  nicechart.py
#
#  Copyright 2011 
#  
#  Christoph Sterz 
#  Florian Weber 
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  




# These two lines are only needed if you don't put the script directly into
# the installation directory
#import sys
#sys.path.append('/usr/share/inkscape/extensions')

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *
import math, re, nicechart_colors as nc_colors

csv_file_name=""

class NiceChart(inkex.Effect):
	"""
	Example Inkscape effect extension.
	Creates a new layer with a "Hello World!" text centered in the middle of the document.
	"""
	def __init__(self):
		"""
		Constructor.
		Defines the "--what" option of a script.
		"""
		# Call the base class constructor.
		inkex.Effect.__init__(self)
		
		# Define string option "--what" with "-w" shortcut and default chart values.
		self.OptionParser.add_option('-w', '--what', action = 'store',
			  type = 'string', dest = 'what', default = '22,11,67',
			  help = 'Chart Values')
	 	
		# Define string option "--type" with "-t" shortcut.
		self.OptionParser.add_option("-t", "--type", action="store",
			  type="string", dest="type", default='',
			  help="Chart Type")
		
		# Define bool option "--blur" with "-b" shortcut.
	 	self.OptionParser.add_option("-b", "--blur", action="store",
			  type="inkbool", dest="blur", default='True',
			  help="Blur Type")
		
		# Define string option "--file" with "-f" shortcut.
	 	self.OptionParser.add_option("-f", "--filename", action="store",
			  type="string", dest="filename", default='',
			  help="Name of File")
		
		# Define string option "--input_type" with "-i" shortcut.
	 	self.OptionParser.add_option("-i", "--input_type", action="store",
			  type="string", dest="input_type", default='file',
			  help="Chart Type")
		
		# Define string option "--delimiter" with "-d" shortcut.
	 	self.OptionParser.add_option("-d", "--delimiter", action="store",
			  type="string", dest="csv_delimiter", default=';',
			  help="delimiter")
			  
		# Define string option "--colors" with "-c" shortcut.
	 	self.OptionParser.add_option("-c", "--colors", action="store",
			  type="string", dest="colors", default='default',
			  help="color-scheme")
		
		
	 	self.OptionParser.add_option("-k", "--col_key", action="store",
			  type="int", dest="col_key", default='0',
			  help="column that contains the keys")
		
		
	 	self.OptionParser.add_option("-v", "--col_val", action="store",
			  type="int", dest="col_val", default='1',
			  help="column that contains the values")
			  
	 	self.OptionParser.add_option("-r", "--rotate", action="store",
			  type="inkbool", dest="rotate", default='False',
			  help="Draw barchart horizontally")
			
	 	self.OptionParser.add_option("-W", "--bar-width", action="store",
			type="int", dest="bar_width", default='10',
			help="width of bars")
			
	 	self.OptionParser.add_option("-H", "--bar-height", action="store",
			type="int", dest="bar_height", default='100',
			help="height of bars")
			
	 	self.OptionParser.add_option("-O", "--bar-offset", action="store",
			type="int", dest="bar_offset", default='5',
			help="distance between bars")
			
	 	self.OptionParser.add_option("-o", "--stacked-bar-text-offset", action="store",
			type="int", dest="stacked_bar_text_offset", default='10',
			help="distance between stacked bar and descriptions")
			
	 	self.OptionParser.add_option("-F", "--font", action="store",
			type="string", dest="font", default='sans-serif',
			help="font of description")
			
		#Dummy:
		self.OptionParser.add_option("","--input_sections")
	
	
	def effect(self):
		"""
		Effect behaviour.
		Overrides base class' method and inserts a nice looking chart into SVG document.
		"""
		# Get script's "--what" option value and process the data type --- i concess the if term is a little bit of magic
		what = self.options.what
		keys=[]
		values=[]
		keys_present=True
		
		csv_file_name=self.options.filename
		csv_delimiter=self.options.csv_delimiter
		input_type=self.options.input_type
		col_key=self.options.col_key
		col_val=self.options.col_val
		
		if(input_type=="\"file\""):
			csv_file=open(csv_file_name,"r")
			for line in csv_file:
				if(line==""):
					#ignore empty lines:
					continue
					value=line.split(csv_delimiter)
					keys.append(value[col_key])
					values.append(value[col_val])
			csv_file.close()
		elif(input_type=="\"direct_input\""):
			what=re.findall("([A-Z|a-z|0-9]+:[0-9]+)",what)
			for value in what:
				value=value.split(":")
				keys.append(value[0])
				values.append(float(value[1]))
		else:
			err_log=open("/home/florian/err.log","a")
			err_log.write("Error: input_type="+input_type+"\n")
			err_log.close()

		# Get script's "--type" option value.
		charttype=self.options.type
		
		# Get access to main SVG document element and get its dimensions.
		svg = self.document.getroot()
		
		# Get the page attibutes:
		width  = inkex.unittouu(svg.get('width'))
		height = inkex.unittouu(svg.attrib['height'])
		
		# Create a new layer.
		layer = inkex.etree.SubElement(svg, 'g')
		layer.set(inkex.addNS('label', 'inkscape'), 'Chart %s Layer' % (what))
		layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
		
		# Check if Blur should be drawn:
		draw_blur=self.options.blur
		
		# Set Default Colors
		Colors=self.options.colors
		if(Colors[0].isalpha()):
			Colors=nc_colors.get_color_scheme(Colors)
		else:
			Colors=re.findall("(#[0-9a-fA-F]{6})",Colors)
		
		color_count=len(Colors)
		
		#Those values should be self-explaining:
		bar_height=self.options.bar_height
		bar_width=self.options.bar_width
		bar_offset=self.options.bar_offset
		#offset of the description in stacked-bar-charts:
		stacked_bar_text_offset=self.options.stacked_bar_text_offset
		
		#get font
		font=self.options.font
		
		#get rotation
		rotate = self.options.rotate	




		if(charttype=="bar"):
		#########
		###BAR###
		#########
			
			#iterate all values, use offset to draw the bars in different places
			offset=0
			color=0
			
			# Normalize the bars to the largest value
			try:
				value_max=max(values)
			except ValueError:
				value_max=0.0

			for x in range(len(values)):
				values[x]=(float(values[x])/value_max)*bar_height
			
			# Get defs of Document
			defs = self.xpathSingle('/svg:svg//svg:defs')
			if defs == None:
				defs = inkex.etree.SubElement(self.document.getroot(),inkex.addNS('defs','svg'))
				
			# Create new Filter
			filt = inkex.etree.SubElement(defs,inkex.addNS('filter','svg'))
			filtId = self.uniqueId('filter')
			self.filtId = 'filter:url(#%s);' % filtId
			for k, v in [('id', filtId), ('height', "3"),
						 ('width', "3"),
						 ('x', '-0.5'), ('y', '-0.5')]:
				filt.set(k, v)
			
			# Append Gaussian Blur to that Filter
			fe = inkex.etree.SubElement(filt,inkex.addNS('feGaussianBlur','svg'))
			fe.set('stdDeviation', "1.1")
			 
			# Draw Single bars with their shadows
			for value in values:
				
				#draw blur, if it is wanted
				if(draw_blur):
					# Create shadow element
					shadow = inkex.etree.Element(inkex.addNS("rect","svg"))
					# Set chart position to center of document. Make it horizontal or vertical
					if(not rotate):
						shadow.set('x', str(width / 2 + offset +1))
						shadow.set('y', str(height / 2 - int(value)+1))
					else:
						shadow.set('y', str(width / 2 + offset +1))
						shadow.set('x', str(height / 2 +1))
					# Set shadow properties
					if(not rotate):
						shadow.set("width", str(bar_width))
						shadow.set("height", str(int(value)*1))
					else:
						shadow.set("height", str(bar_width))
						shadow.set("width", str(int(value)*1))
					# Set shadow blur (connect to filter object in xml path)
					shadow.set("style","filter:url(#filter)")
				
				# Create rectangle element
				#shadow = inkex.etree.Element(inkex.addNS("rect","svg"))
				rect = inkex.etree.Element(inkex.addNS('rect','svg'))
				
				# Set chart position to center of document.
				if(not rotate):
					rect.set('x', str(width/2+offset))
					rect.set('y', str(height/2-int(value)))
				else:
					rect.set('y', str(width/2+offset))
					rect.set('x', str(height/2))
				# Set rectangle properties
				if(not rotate):
					rect.set("width", str(bar_width))
					rect.set("height", str(int(value)*1))
				else:
					rect.set("height", str(bar_width))
					rect.set("width", str(int(value)*1))
					
				rect.set("style","fill:"+Colors[color%color_count])
				
				# Set shadow blur (connect to filter object in xml path)
				if(draw_blur):
					shadow.set("style","filter:url(#filter)")
				
				
				# If keys are given create text elements
				if(keys_present):
					text = inkex.etree.Element(inkex.addNS('text','svg'))
					if(not rotate):
						text.set("transform","matrix(0,-1,1,0,0,0)") #textrotation
						text.set("x", "-"+str(height/2+2))
						text.set("y", str(width/2+offset+bar_width*0.75))
					else:
						text.set("y", str(width/2+offset+bar_width*0.75))
						text.set("x", str(height/2-2))						
					
					text.set("style","font-size:"+str(bar_width)\
					+"px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-family:"\
					+font+";-inkscape-font-specification:Bitstream   Charter;text-align:end;text-anchor:end")

					text.text=keys[color]
					

				# Increase Offset and Color
				offset=offset+bar_width+bar_offset
				color=(color+1)%8
				# Connect elements together.
				if(draw_blur):
					layer.append(shadow)
				layer.append(rect)
				if(keys_present):
					layer.append(text)
		#End Bar
		
		
		
		elif(charttype=="pie"):
		#########
		###PIE###
		#########
			# Iterate all values to draw the different slices
			color=0
			
			# Set Default Colors
			
			# Get defs of Document
			defs = self.xpathSingle('/svg:svg//svg:defs')
			if defs == None:
					defs = inkex.etree.SubElement(self.document.getroot(),inkex.addNS('defs','svg'))
				
			# Create new Filter
			filt = inkex.etree.SubElement(defs,inkex.addNS('filter','svg'))
			filtId = self.uniqueId('filter')
			self.filtId = 'filter:url(#%s);' % filtId
			for k, v in [('id', filtId), ('height', "3"),
						 ('width', "3"),
						 ('x', '-0.5'), ('y', '-0.5')]:
				filt.set(k, v)
			# Append Gaussian Blur to that Filter
			fe = inkex.etree.SubElement(filt,inkex.addNS('feGaussianBlur','svg'))
			fe.set('stdDeviation', "1.1")
			
			# Add a grey background circle
			background=inkex.etree.Element(inkex.addNS("circle","svg"))
			background.set("cx", str(width/2))
			background.set("cy", str(height/2))
			background.set("r", "50")
			background.set("style","fill:#aaaaaa;stroke:none")
			layer.append(background)
			
			#create value sum in order to divide the slices
			try:
				valuesum=sum(values)
			except ValueError:
				valuesum=0
			
			# Set an offsetangle
			offset=0
			
			# Draw single slices with their shadow
			for value in values:
				# Calculate the PI-angles for start and end
				angle=(2*3.141592)/valuesum*int(value)
				
				# Create the shadow first (if it should be created):
				if(draw_blur):
					shadow=inkex.etree.Element(inkex.addNS("path","svg"))
					shadow.set(inkex.addNS('type', 'sodipodi'), 'arc')
					shadow.set(inkex.addNS('cx', 'sodipodi'), str(width/2))
					shadow.set(inkex.addNS('cy', 'sodipodi'), str(height/2))
					shadow.set(inkex.addNS('rx', 'sodipodi'), "50")
					shadow.set(inkex.addNS('ry', 'sodipodi'), "50")
					shadow.set(inkex.addNS('start', 'sodipodi'), str(offset))
					shadow.set(inkex.addNS('end', 'sodipodi'), str(offset+angle))
					shadow.set("style","filter:url(#filter);fill:#000000")
				
				#then add the slice
				pieslice=inkex.etree.Element(inkex.addNS("path","svg"))
				pieslice.set(inkex.addNS('type', 'sodipodi'), 'arc')
				pieslice.set(inkex.addNS('cx', 'sodipodi'), str(width/2))
				pieslice.set(inkex.addNS('cy', 'sodipodi'), str(height/2))
				pieslice.set(inkex.addNS('rx', 'sodipodi'), "50")
				pieslice.set(inkex.addNS('ry', 'sodipodi'), "50")
				pieslice.set(inkex.addNS('start', 'sodipodi'), str(offset))
				pieslice.set(inkex.addNS('end', 'sodipodi'), str(offset+angle))
				pieslice.set("style","fill:"+Colors[color%color_count]+";stroke:none;fill-opacity:1")
				
				#If text is given, draw short paths and add the text
				if(keys_present):
					path=inkex.etree.Element(inkex.addNS("path","svg"))
					path.set("d","m "+str((width/2)+50*math.cos(angle/2+offset))\
					+","+str((height/2)+50*math.sin(angle/2+offset))\
					+" "+str(8*math.cos(angle/2+offset))+","+str(8*math.sin(angle/2+offset)))

					path.set("style","fill:none;stroke:#000000;stroke-width:1px;"\
							"stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1")

					layer.append(path)
					text = inkex.etree.Element(inkex.addNS('text','svg'))
					text.set("x", str((width/2)+60*math.cos(angle/2+offset)))
					text.set("y", str((height/2)+60*math.sin(angle/2+offset)))
					#check if it is right or left of the Pie
					if(math.cos(angle/2+offset)>0):
						text.set("style","font-size:10px;font-style:normal;font-variant:normal;"\
								"font-weight:normal;font-stretch:normal;font-family:"\
								+font+";-inkscape-font-specification:Bitstream Charter")

					else:
						text.set("style","font-size:10px;font-style:normal;font-variant:normal;"\
								"font-weight:normal;font-stretch:normal;font-family:"\
								+font+";-inkscape-font-specification:Bitstream Charter;"\
								"text-align:end;text-anchor:end")
					
					text.text=keys[color]
					layer.append(text)
				
				#increase the rotation-offset and the colorcycle-position
				offset=offset+angle
				color=(color+1)%8
				
				#append the objects to the extension-layer
				if(draw_blur):
					layer.append(shadow)
				layer.append(pieslice)
		#End Pie	



	
		elif(charttype=="stbar"):
		#################
		###STACKED BAR###
		#################
			# Iterate all values to draw the different slices
			color=0
			
			
			
			# Get defs of Document
			defs = self.xpathSingle('/svg:svg//svg:defs')
			if defs == None:
					defs = inkex.etree.SubElement(self.document.getroot(),inkex.addNS('defs','svg'))
				
			# Create new Filter
			filt = inkex.etree.SubElement(defs,inkex.addNS('filter','svg'))
			filtId = self.uniqueId('filter')
			self.filtId = 'filter:url(#%s);' % filtId
			for k, v in [('id', filtId), ('height', "3"),
						 ('width', "3"),
						 ('x', '-0.5'), ('y', '-0.5')]:
				filt.set(k, v)
			# Append Gaussian Blur to that Filter
			fe = inkex.etree.SubElement(filt,inkex.addNS('feGaussianBlur','svg'))
			fe.set('stdDeviation', "1.1")
			
			#create value sum in order to divide the bars
			try:
				valuesum=sum(values)
			except ValueError:
				valuesum=0.0

			for value in values:
				valuesum=valuesum+float(value)
			
			# Init offset
			offset=0
			   
			# Draw Single bars with their shadows
			for value in values:
				
				# Calculate the individual heights normalized on 100units
				normedvalue=(bar_height/valuesum)*float(value)
				
				if(draw_blur):
					# Create rectangle element
					shadow = inkex.etree.Element(inkex.addNS("rect","svg"))
					# Set chart position to center of document.
					shadow.set('x', str(width / 2 + 1))
					shadow.set('y', str(height / 2 - offset - (normedvalue)+1)) 
					# Set rectangle properties
					shadow.set("width",str(bar_width))
					shadow.set("height", str((normedvalue)))
					# Set shadow blur (connect to filter object in xml path)
					shadow.set("style","filter:url(#filter)")
				
				# Create rectangle element
				rect = inkex.etree.Element(inkex.addNS('rect','svg'))
				
				# Set chart position to center of document.
				rect.set('x', str(width / 2 ))
				rect.set('y', str(height / 2 - offset - (normedvalue)))
			   
				# Set rectangle properties
				rect.set("width", str(bar_width))
				rect.set("height", str((normedvalue)))
				rect.set("style","fill:"+Colors[color%color_count])
				
				#If text is given, draw short paths and add the text
				if(keys_present):
					path=inkex.etree.Element(inkex.addNS("path","svg"))
					path.set("d","m "+str((width+bar_width)/2)+","+str(height / 2 - offset - (normedvalue / 2))+" "+str(bar_width/2+stacked_bar_text_offset)+",0")
					path.set("style","fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1")
					layer.append(path)
					text = inkex.etree.Element(inkex.addNS('text','svg'))
					text.set("x", str(width/2+bar_width+stacked_bar_text_offset+1))
					text.set("y", str(height / 2 - offset + 2 - (normedvalue / 2)))
					text.set("style","font-size:10px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-family:"+font+";-inkscape-font-specification:Bitstream Charter")
					text.text=keys[color]
					layer.append(text)
				
				
				# Increase Offset and Color
				offset=offset+normedvalue
				color=(color+1)%8
				
				# Connect elements together.
				if(draw_blur):
					layer.append(shadow)
				layer.append(rect)
		#End StackedBarChart

# Create effect instance and apply it.
effect = NiceChart()
effect.affect()
