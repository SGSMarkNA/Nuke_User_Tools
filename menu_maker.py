from . import USER_MODULES_NAMES,USER_MENUS,USER_TOOLS_MENU

def find_User_Module_Name(function):
	for name in function.__module__.split("."):
		if name in USER_MENUS.keys():
			return USER_MENUS[name]

def make_Nice_Function_Name(function):
	return function.__name__.replace("_"," ")
	
def Add_Command(function,shortcut_key=None):
	user_menu = find_User_Module_Name(function)
	function_name = make_Nice_Function_Name(function)
	if shortcut_key == None:
		user_menu.addCommand(function_name,lambda:function())
	else:
		user_menu.addCommand(function_name,lambda:function(),shortcut_key)