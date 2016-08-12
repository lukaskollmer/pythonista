"""
Use this module to change the editor and console font programatically
"""

__author__ = "Lukas Kollmer<lukas.kollmer@gmail.com>"
__copyright__ = "Copyright (c) 2016 Lukas Kollmer<lukas.kollmer@gmail.com>"

from pythonista import _utils
from pythonista import defaults

_utils.guard_objc_util()

import objc_util
import ctypes

# --- Custom Fonts

UIFont = objc_util.ObjCClass("UIFont")
OMBarButton = objc_util.ObjCClass('OMBarButton')
UIButton = objc_util.ObjCClass('UIButton')

PA2UniversalTextEditorViewController = objc_util.ObjCClass("PA2UniversalTextEditorViewController")


CTFontManagerRegisterFontsForURL = objc_util.c.CTFontManagerRegisterFontsForURL
CTFontManagerRegisterFontsForURL.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool

CFURLCreateWithString = objc_util.c.CFURLCreateWithString
CFURLCreateWithString.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
CFURLCreateWithString.restype = ctypes.c_void_p



def load_custom_font(file):
	#https://marco.org/2012/12/21/ios-dynamic-font-loading
	font_url = CFURLCreateWithString(None, objc_util.ns(file), None)
	
	error = ctypes.c_void_p(None)
	success = CTFontManagerRegisterFontsForURL(objc_util.ObjCInstance(font_url), 0, ctypes.byref(error))
	#print(objc_util.ObjCInstance(error))
	#print("success:", success)
	
	#font = UIFont.fontWithName_size_("SFMono-Regular", 15)
	#print(font)

def set_editor_font(name, size=15):
	"""
	NOTE: This still requires a restart
	"""
	defaults.set("EditorFontName", name)
	defaults.set("EditorFontSize", size)
	
	#font = objc_util.UIFont.fontWithName_size_(name, size)

# --- Custom Button Items

_DEFAULT_BAR_BUTTON_POSITION = "left"

UIBarButtonItem = objc_util.ObjCClass('UIBarButtonItem')

def _add_button_item(item, position=_DEFAULT_BAR_BUTTON_POSITION):
	"""
	Do not call this directly, it just adds the item to the view.
	You'll need to add the action to the view manually
	"""
	tabVC = _utils._application.keyWindow().rootViewController().detailViewController()
	
	if position == "left":
		buttonItems = tabVC.persistentLeftBarButtonItems().mutableCopy()
		buttonItems.insert(Object=item, atIndex=0)
		tabVC.setPersistentLeftBarButtonItems_(buttonItems)
		tabVC.reloadBarButtonItemsForSelectedTab()
	elif position == "right":
		toolbar = tabVC.toolbar()
		button = UIButton.new()
		button.setTitle_("title")
		toolbar.addSubview_(button)
	


def add_text_button_item(text, action, position=_DEFAULT_BAR_BUTTON_POSITION):
	tabVC = _utils._application.keyWindow().rootViewController().detailViewController()
	selector = _utils.add_method(action, tabVC)
	
	barButtonItem = UIBarButtonItem.alloc().init(Title=text, style=0, target=tabVC, action=selector)
	#print(barButtonItem)
	_add_button_item(barButtonItem, position)

def add_image_button_item(image, action, position=_DEFAULT_BAR_BUTTON_POSITION):
	barButtonItem = UIBarButtonItem.alloc().init(Image=image, style=0, target=tabVC, action=selector)
	#print(barButtonItem)
	_add_button_item(barButtonItem, position)


# --- Editor Keyboard Shortcuts

UIKeyCommand = objc_util.ObjCClass('UIKeyCommand')
PASlidingContainerViewController = objc_util.ObjCClass('PASlidingContainerViewController')

_UIKeyModifierAlphaShift = 1 << 16
_UIKeyModifierShift      = 1 << 17
_UIKeyModifierControl    = 1 << 18
_UIKeyModifierAlternate  = 1 << 19
_UIKeyMofifierCommand    = 1 << 20
_UIKeyModifierNumericPad = 1 << 21


_modifiers_map = {
	"cmd":      _UIKeyMofifierCommand,
	"capslock": _UIKeyModifierAlphaShift,
	"shift":    _UIKeyModifierShift,
	"control":  _UIKeyModifierControl,
	"alt":      _UIKeyModifierAlternate,
	"num":      _UIKeyModifierNumericPad
}

def register_shortcut(shortcut, action=None, title=None):
	"""
	Note: this shortcut works only when the editor is in focus. (no idea why)
	For some reason i, b, u dont work (http://www.openradar.me/25463955p\)
	"""
	
	rootVC = _utils._application.keyWindow().rootViewController()
	
	if isinstance(shortcut, objc_util.ObjCInstance):
		if shortcut.isKindOfClass_(UIKeyCommand):
			rootVC.addKeyCommand_(shortcut)
			return shortcut
	keys = shortcut.split("+")
	_modifiers = keys[:-1]
	input = keys[-1].upper()
	
	modifiers = (0 << 00)
	for modifier in _modifiers:
		modifiers |= _modifiers_map[modifier.lower()]
	
	
	selector = _utils.add_method(action, rootVC)
	keyCommand = UIKeyCommand.keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(input, modifiers, selector, title)
	
	rootVC.addKeyCommand_(keyCommand)
	
	return keyCommand

def deregister_shortcut(command):
	rootVC = _utils._application.keyWindow().rootViewController()
	rootVC.removeKeyCommand_(command)

# --- Tab Management
def close_tab(tab):
	if isinstance(tab, objc_util.ObjCInstance):
		if tab.isKindOfClass_(PA2UniversalTextEditorViewController):
			tabVC = _utils._application.keyWindow().rootViewController().detailViewController()
			tabVC.closeTab_(tab)
	if isinstance(tab, int):
		tabVC = _utils._application.keyWindow().rootViewController().detailViewController()
		tab = tabVC.tabViewControllers()[tab]
		print(tab)
		close_tab(tab)

def close_current_tab():
	import editor
	tab = editor._get_editor_tab()
	close_tab(tab)

def open_tab(path=None):
	tabVC = _utils._application.keyWindow().rootViewController().detailViewController()
	if path is None:
		tabVC.addTab_(None)
	else:
		import editor
		#tabVC.open(File=path, inNewTab=True, withPreferredEditorType=True, forceReload=False)
		editor.open_file(path, new_tab=True, force_reload=False)
	

# --- Quick Open

def show_quick_open():
	pass
	

# --- Demo
if __name__ == "__main__":
	
	# Test custom fonts
	import os
	font_path = "file://" + os.path.expanduser("~/Documents/Fonts/SFMono/SFMono-Regular.otf")
	
	#load_custom_font(font_path)
	
	font_name = "Menlo-Regular"
	#set_editor_font(font_name, 15)
	
	
	# Test bar buttons
	def button_action(_self, _sel):
		print("button tapped!!!")
	add_text_button_item("hi", button_action, "left")
	
	
	# Test keyboard shortcuts
	def commandGHandler(_self, _sel):
		print("Command G pressed")
	
	register_shortcut("cmd+g", commandGHandler, "")
	
