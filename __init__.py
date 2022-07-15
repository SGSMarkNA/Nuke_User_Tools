import nuke
import os

def get_user_tool_module_Names():
	root_path = os.path.dirname(__file__)
	r,names,files = next(os.walk(root_path))
	return names

def make_user_tool_module_menus(user_tools_menu,names):
	User_Menus = {}
	for name in names:
		menu = user_tools_menu.addMenu(name.replace("_"," "))
		User_Menus[name]=menu
	return User_Menus

def import_user_modules(names):
	message = ""
	for module in names:
		try:
			__import__(__name__+"."+module)
		except:
			message += "Was Unable to Load The User Tools for %s\n" % module
	
	if len(message):
		nuke.message(message)

#USER_TOOLS_MENU    = nuke.menu("Nuke").addMenu("User Tools")
#USER_MODULES_NAMES = get_user_tool_module_Names()
#USER_MENUS         = make_user_tool_module_menus(USER_TOOLS_MENU,USER_MODULES_NAMES)
#import_user_modules(USER_MODULES_NAMES)
