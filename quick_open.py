"""
Use this module to fire up the quick open menu (like Xcode)
"""

__author__ = "Lukas Kollmer<lukas.kollmer@gmail.com>"
__copyright__ = "Copyright (c) 2016 Lukas Kollmer<lukas.kollmer@gmail.com>"

from pythonista import _utils
from pythonista import files
from pythonista import editor_util
from pythonista import theme

_utils.guard_objc_util()

import objc_util
import ui
import os

NSIndexPath = objc_util.ObjCClass("NSIndexPath")
UIColor = objc_util.ObjCClass('UIColor')

class QuickOpenTableView (ui.View):
	def __init__(self):
		self.name = "Quick Open"
		
		self.selection_index = 0
		
		self.results = files.search("")
		
		# Reorder to have recents at front
		for item in files.get_recents():
			item_path = os.path.expanduser("~/Documents") + item
			if item_path in self.results:
				self.results.remove(item_path)
				self.results.insert(0, item_path)
		
		
		self.textfield = ui.TextField()
		self.textfield.font = ("<system>", 25)
		self.textfield.placeholder = "Enter a filename ..."
		self.textfield.delegate = self
		self.textfield.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
		self.textfield.autocorrection_type = False
		self.textfield.bordered = False
		self.textfield.background_color = "white"
		
		self.height = 500
		self.width = 500
		
		#self.textfield.frame = (10, 0, self.width - 20, 100)
		self.textfield.height = 100
		self.textfield.width = self.width
		self.add_subview(self.textfield)
		
		side_frame = objc_util.CGRect((0, 0), (10, 100))
		side_view  = objc_util.UIView.alloc().initWithFrame_(side_frame)
		
		objc_textField = objc_util.ObjCInstance(self.textfield).textField()
		
		objc_textField.setLeftView_(side_view)
		objc_textField.setLeftViewMode_(3)
		
		objc_textField.setRightView_(side_view)
		objc_textField.setRightViewMode_(3)
		
		self.tableview = ui.TableView()
		self.tableview.delegate = self
		self.tableview.data_source = self
		self.tableview.frame = (0, self.textfield.height, self.width, self.height - self.textfield.height)
		#self.tableview.background_color = theme.get()['bar_background']
		self.add_subview(self.tableview)
		
		#self.cell_selection_view = objc_util.UIView.alloc().initWithFrame_(objc_util.CGRect((0, 0), (10, 10)))
		#self.cell_selection_view.setBackgroundColor_(UIColor.colorWithHexString_(theme.get()["text_selection_tint"])) #tab_background
		#self.cell_selection_view.background_color = 'red'
		#self.cell_selection_view.setBackgroundColor_(UIColor.redColor()) #tab_background
		
		self.textfield.begin_editing()
		
		self.reload_selection()
		
		def up_arrow(_self, _sel):
			if self.selection_index <= 0:
				return
			else:
				self.selection_index -= 1
				self.reload_selection()
		
		def down_arrow(_self, _sel):
			if (self.selection_index + 1) >= len(self.results):
				return
			else:
				self.selection_index += 1
				self.reload_selection()
		
		self.arrow_up_hook = editor_util.register_shortcut("UIKeyInputUpArrow" , up_arrow)
		self.arrow_down_hook = editor_util.register_shortcut("UIKeyInputDownArrow", down_arrow)
		
		
		# use cmd+w to close this view
		"""def close_button_handler(_self, _sel):
			self.close()
		
		editor_util.deregister_shortcut(cmd_w)
		self.close_hook = editor_util.register_shortcut("cmd+w", close_button_handler, "Close")"""
	
	
	def reload_for_term(self, term):
		self.results = files.search(term, filename=False)
		self.tableview.reload()
		self.selection_index = 0
		if len(self.results) != 0:
			self.reload_selection()
	
	def reload_selection(self):
		index = self.selection_index
		indexPath = NSIndexPath.indexPathFor(row=index, inSection=0)
		objc_util.ObjCInstance(self.tableview).selectRowAtIndexPath_animated_scrollPosition_(indexPath, False, 2)
	
	def textfield_did_change(self, textfield):
		self.reload_for_term(textfield.text)
	
	def textfield_should_return(self, textfield):
		if len(self.results) == 0: return False
		textfield.end_editing()
		self.open_selected_file()
		
		return True
		
	def tableview_number_of_sections(self, tableview):
		return 1
	
	def tableview_number_of_rows(self, tableview, section):
		return len(self.results)
	
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		result = self.results[row]
		cell.text_label.text = os.path.split(result)[1]
		#cell.text_label.text_color = theme.get()["default_text"]
		#cell.background_color = tableview.background_color
		#objc_util.ObjCInstance(cell).selectedBackgroundView().setBackgroundColor_(UIColor.redColor())
		#objc_util.ObjCInstance(cell).setSelectedBackgroundView_(self.cell_selection_view)
		path_view = ui.Label()
		path_view.text = result.replace(os.path.expanduser("~/Documents"), "")
		path_view.font = ("<system>", 12)
		path_view.text_color = "#4e4e4e"
		path_view.frame = (10, cell.height-15, tableview.width-10, 15)
		#path_view.background_color = "red"
		cell.content_view.add_subview(path_view)
		return cell
	
	def tableview_did_select(self, tableview, section, row):
		self.selection_index = row
		self.open_selected_file()
	
	def open_selected_file(self):
		if len(self.results) == 0: return
		file = self.results[self.selection_index]
		editor_util.open_tab(file)
		self.close()
	
	def will_close(self):
		editor_util.deregister_shortcut(self.arrow_up_hook)
		editor_util.deregister_shortcut(self.arrow_down_hook)
		
		"""editor_util.deregister_shortcut(self.close_hook)
		editor_util.register_shortcut(cmd_w)"""
	
	def draw(self):
		pass#print(objc_util.ObjCInstance(self.textfield).layer())

def load():
	quickOpenView = QuickOpenTableView()
	import editor
	#editor.present_themed(quickOpenView, style="sheet")
	#bar_color = theme.get()["bar_background"]
	#title_color = theme.get()["default_text"]
	#quickOpenView.present("sheet", title_bar_color=bar_color, title_color=title_color)
	quickOpenView.present("sheet")

if __name__ == "__main__":
	load()
