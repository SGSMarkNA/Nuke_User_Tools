from PySide.QtGui import *
from PySide.QtCore import *
import os
import sys
import random
try:
	import nuke
except ImportError:
	nuke = None


#HOME_FOLDER = os.path.join(os.path.expanduser("~"), ".nuke")


class RestaurantRandomizer(QWidget):
	''''''

	def __init__(self):
		
		# Initialize the object as a QWidget and
		# set its title and minimum width
		QWidget.__init__(self)
		self.setWindowTitle('Restaurant Randomizer')
		self.setMinimumWidth(400)
		
		p = self.palette()
		p.setColor(self.backgroundRole(), Qt.gray)
		self.setPalette(p)		
		

		# Create the QVBoxLayout that lays out the whole form
		self.layout = QVBoxLayout()

		# Create the form layout that manages the labeled controls
		self.form_layout = QFormLayout()

		# Restaurant Name & URL...
		self.choicesDict = {'Als Famous Deli':'<a href=\"http://www.yelp.com/biz/als-famous-deli-royal-oak\">Als Famous Deli</a>',
		                    'Athens Coney Island':'<a href=\"http://www.yelp.com/biz/athens-coney-island-royal-oak\">Athens Coney Island</a>',
		                    'Five Guys':'<a href=\"http://www.fiveguys.com\">Five Guys</a>',
		                    'Subway':'<a href=\"http://www.subway.com\">Subway</a>',
		                    'Jersey Mikes':'<a href=\"http://www.jerseymikes.com\">Jersey Mikes</a>',
		                    'Jets Pizza':'<a href=\"http://jetspizza.com\">Jets Pizza</a>',
		                    'Primos Pizza':'<a href=\"http://www.primosbirmingham.com\">Primos Pizza</a>',
		                    'KFC':'<a href=\"https://www.kfc.com\">KFC</a>',
		                    'Beyond Juicery':'<a href=\"http://www.beyondjuicedetroit.com\">Beyond Juicery</a>',
		                    'Bagel Factory':'<a href=\"http://www.yelp.com/biz/bagel-factory-cafe-birmingham\">Bagel Factory</a>',
		                    'Jimmy Johns':'<a href=\"http://www.jimmyjohns.com\">Jimmy Johns</a>',
		                    'Potbelly':'<a href=\"http://www.potbelly.com/Shops/ShopLocator.aspx?PotbellyShopId=065\">Potbelly</a>',
		                    'Brooklyn Pizza':'<a href=\"http://www.brooklynpizzaonline.com\">Brooklyn Pizza</a>',
		                    'Hunter House Burgers':'<a href=\"http://www.hunterhousehamburgers.com\">Hunter House Burgers</a>',
		                    'Whistle Stop':'<a href=\"http://www.whistlestopdiners.com\">Whistle Stop</a>',
		                    'Original House of Pancakes':'<a href=\"http://www.originalpancakehouse.com\">Original House of Pancakes</a>',
		                    'Greek Islands Coney':'<a href=\"http://www.greekislandsconey.com/birmingham\">Greek Islands Coney</a>',
		                    'Panera Bread':'<a href=\"http://www.panerabread.com\">Panera Bread</a>',
		                    'Griffen Claw':'<a href=\"http://www.griffinclawbrewingcompany.com\">Griffen Claw</a>',
		                    'Pita Cafe':'<a href=\"http://www.thepitacafe.com\">Pita Cafe</a>',
		                    'Cosi':'<a href=\"https://www.getcosi.com\">Cosi</a>',
		                    'Rojo Mexican Bistro':'<a href=\"http://www.rojomexicanbistro.com\">Rojo Mexican Bistro</a>',
		                    'Mountain King Chinese':'<a href=\"http://places.singleplatform.com/mountain-king-chinese-restaurant/menu\">Mountain King Chinese</a>',
		                    'Pizza Hut':'<a href=\"https://order.pizzahut.com/locations/michigan/birmingham/029824\">Pizza Hut</a>',
		                    'Hungry Howies Pizza':'<a href=\"http://www.hungryhowies.com/store/hungry-howies-1017\">Hungry Howies Pizza</a>',
		                    'Shawarma Kingdom':'<a href=\"https://www.grubhub.com/restaurant/shawarma-kingdom-33757-woodward-ave-birmingham/320781\">Shawarma Kingdom</a>',
		                    'Chipotle':'<a href=\"http://www.chipotle.com\">Chipotle</a>',
		                    'The Big Salad':'<a href=\"http://www.thebigsalad.net/\">The Big Salad</a>',
		                    'Moes Southwest Grill':'<a href=\"http://www.moes.com\">Moes Southwest Grill</a>',
		                    'Shake Shack':'<a href=\"https://www.shakeshack.com\">Shake Shack</a>',
		                    'Chick-fil-A':'<a href=\"https://www.chick-fil-a.com\">Chick-fil-A</a>',
		                    'Whole Foods Market':'<a href=\"https://www.wholefoodsmarket.com\">Whole Foods Market</a>',
		                    'National Coney Island':'<a href=\"http://www.nationalconeyisland.com\">National Coney Island</a>',
		                    'Nicky D\'s Coney Island':'<a href=\"https://www.facebook.com/NickyDsWoodward\">Nicky D\'s Coney Island</a>',
		                    'Grape Leaves':'<a href=\"http://grapeleavesrestaurant.com\">Grape Leaves</a>'
		                    }	

		##----------------------------------------------------------------------##
		# Add an AW logo image...
		print(__file__)
		if os.name == 'nt':
			filepath = __file__
			parent_dir = os.path.abspath(os.path.join(filepath, os.pardir))
			self.curr_dir = parent_dir + '\\' + 'spaceLOGOS_100px.png'
		elif os.name == 'posix':
			filepath = __file__
			parent_dir = os.path.abspath(os.path.join(filepath, os.pardir))
			self.curr_dir = parent_dir + '/' + 'spaceLOGOS_100px.png'
		print(self.curr_dir)
			
		self.pixmap = QPixmap(str(self.curr_dir))
		self.logo = QLabel(self)
		self.logo.setPixmap(self.pixmap)
		# Make QLabel use the whole widget width... (Need this for Nuke's older PySide, which doesn't seem to do this automatically...)
		self.logo.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		# Center the result...
		self.logo.setAlignment(Qt.AlignLeft)
		#self.form_layout.addRow('Result:', self.result)
		self.form_layout.addRow('', self.logo)		
		##----------------------------------------------------------------------##
		# Create and add the label to display the result...
		self.result = QLabel(self)
		self.result.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		self.result.setAlignment(Qt.AlignCenter)
		self.form_layout.addRow(self.result)
		##----------------------------------------------------------------------##
		# Add a clickable URL...
		self.URL = QLabel(self)
		self.URL.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		self.URL.setAlignment(Qt.AlignCenter)
		self.URL.setOpenExternalLinks(True)
		self.form_layout.addRow(self.URL)
		##----------------------------------------------------------------------##
		# Create an empty row...
		self.empty_row = QLabel(self)
		self.empty_row.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		self.empty_row.setAlignment(Qt.AlignCenter)
		self.form_layout.addRow(self.empty_row)		
		##----------------------------------------------------------------------##
		# Add the form layout to the main VBox layout...
		self.layout.addLayout(self.form_layout)
		##----------------------------------------------------------------------##
		# Create a horizontal box layout to hold the button...
		self.button_box = QHBoxLayout()
		# Create the pushbutton with its label...
		self.choice_button = QPushButton("What's for lunch?" , self)
		# Connect the button's clicked signal to show_result...
		self.choice_button.clicked.connect(self.show_result)
		# Add it to the button box...
		self.button_box.addWidget(self.choice_button)
		# Add the button box to the bottom of the main VBox layout...
		self.layout.addLayout(self.button_box)
		##----------------------------------------------------------------------##
		# Set the VBox layout as the window's main layout...
		self.setLayout(self.layout)

	@Slot()
	def show_result(self):
		''' Show the constructed greeting. '''
		self.suggestion = random.choice(list(self.choicesDict.keys()))

		self.URL.setText(self.choicesDict.get(self.suggestion))

		self.empty_row.setText('')

		print(("Today, we will eat " + self.suggestion + " for lunch!"))



if not nuke:
	'''
	If we were not able to import nuke, just make this a standalone panel...
	'''
	app = QApplication(sys.argv)
	panel = RestaurantRandomizer()
	panel.show()
	panel.raise_()
	#app.exec_()
	sys.exit(app.exec_())
	
else:
	'''
	Otherwise, we are probably wanting to run the panel inside of Nuke.
	So, use this start() function as a way to fire up the panel...
	'''
	def start():
		start.panel = RestaurantRandomizer()
		start.panel.show()
		start.panel.raise_()

	start()

