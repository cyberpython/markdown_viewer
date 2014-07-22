#!/usr/bin/env python

'''
The MIT License (MIT)

Copyright (c) 2014 Georgios Migdos  <cyberpython@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

'''

Simple python3 + GTK3 based Markdown viewer.

The application can also open 'Compressed Markdown Files', which are regular ZIP 
archives with the extension '.mdz' that contain a markdown file in their root
 named with the same name as the ZIP archive. 
For example the archive named 'test.mdz' should contain a Markdown file named
'test.md' in its root along with any other files (e.g. images) the Markdown file 
references (each placed in the correct relative path).

The generated HTML document will try to load the following CSS files:

- file:///usr/share/markdown_viewer/style.css (on Linux) or file://<script_dir>/css/style.css (on Windows)


- all '.css' files in the same directory with the Markdown file except 'style.css' 
  in ascending alphabetical order

- style.css

The bundled JQuery, TOC.js and markdown_viewer.js  are the first scripts that are loaded.

The generated HTML5 document will try to load any '.js' files in the same 
directory with the Markdown file in ascending alphabetical order.


Highlighted code by the codehilite extension is assigned the '.code' CCS class.

python-markdown is used for parsing.
webkit is used for rendering.
jquery and toc.js are used to display the table of contents.
'''

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import WebKit
import codecs
import markdown
import urllib
import os
import sys
import tempfile
import zipfile
import subprocess
import platform

PLATFORM = platform.system().lower()

RESOURCE_PATH_BASE_URL = "/usr/share/markdown_viewer"
FILE_PROTO = "file://"


if PLATFORM == "windows":
    FILE_PROTO = "file:"
    RESOURCE_PATH_BASE_URL = urllib.pathname2url(os.path.join(sys.prefix, "res"))

UI_INFO = """
<ui>
   <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileLoad' />
      <menuitem action='FileReload' />
      <separator />
      <menuitem action='FileQuit' />
    </menu>
    <menu action='EditMenu'>
      <menuitem action='EditFind' />
      <menuitem action='EditFindNext' />
      <menuitem action='EditFindPrev' />
    </menu>
    <menu action='ViewMenu'>
      <menuitem action='ViewTOC' />
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='FileLoad' />
    <toolitem action='FileReload' />
  </toolbar>
</ui>
"""

HTML_PRE = """<!DOCTYPE html>
<html>

  <head>
    <meta charset="utf-8" />
    <title>Untitled</title>
    <link rel="stylesheet" type="text/css" href='"""+FILE_PROTO+RESOURCE_PATH_BASE_URL+"""/style.css' />
    <link rel="stylesheet" type="text/css" href='"""+FILE_PROTO+RESOURCE_PATH_BASE_URL+"""/toc.css' />
"""

HTML_STYLE = """
    <link rel="stylesheet" type="text/css" href="style.css" />
    
    
    <script src='"""+FILE_PROTO+RESOURCE_PATH_BASE_URL+"""/jquery.js'></script>
    <script src='"""+FILE_PROTO+RESOURCE_PATH_BASE_URL+"""/toc.js'></script>
    <script src='"""+FILE_PROTO+RESOURCE_PATH_BASE_URL+"""/markdown_viewer.js'></script>
    
"""

HTML_MID = """
  </head>

  <body>
    <div id='markdown_content'>
"""

HTML_POST = """
    </div>
  </body>

</html>"""

class MarkdownViewer():

    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_default_size(800, 600)
        self.last_loaded_file = None
        self.doc_dir = None # Temp dir to unzip compressed documents
        self.window.set_title("Markdown Viewer")
        
        action_group = Gtk.ActionGroup("markdown_viewer_actions")
        
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)
        
        action_editmenu = Gtk.Action("EditMenu", "Edit", None, None)
        action_group.add_action(action_editmenu)
        
        action_viewmenu = Gtk.Action("ViewMenu", "View", None, None)
        action_group.add_action(action_viewmenu)
        
        action_load = Gtk.Action("FileLoad", "_Load",
            "Load a file", Gtk.STOCK_OPEN)
        action_load.connect("activate", self.on_load_file)
        action_group.add_action_with_accel(action_load, "<Ctrl>o")
        
        self.action_reload = Gtk.Action("FileReload", "_Reload",
            "Reload current file", Gtk.STOCK_REFRESH)
        self.action_reload.connect("activate", self.on_reload_file)
        action_group.add_action_with_accel(self.action_reload, "<Ctrl>r")
        self.action_reload.set_sensitive(False)
        
        self.action_quit = Gtk.Action("FileQuit", "_Quit",
            "Quit", Gtk.STOCK_QUIT)
        self.action_quit.connect("activate", self.on_quit)
        action_group.add_action_with_accel(self.action_quit, "<Ctrl>q")
        
        self.action_edit_find = Gtk.Action("EditFind", "_Find",
            "Search for text", None)
        self.action_edit_find.connect("activate", self.on_find)
        action_group.add_action_with_accel(self.action_edit_find, "<Ctrl>f")
        
        self.action_edit_find_next = Gtk.Action("EditFindNext", "Find _next",
            "Find next", None)
        self.action_edit_find_next.connect("activate", self.on_find_next)
        action_group.add_action_with_accel(self.action_edit_find_next, "F3")
        
        self.action_edit_find_prev = Gtk.Action("EditFindPrev", "Find _previous",
            "Find previous", None)
        self.action_edit_find_prev.connect("activate", self.on_find_prev)
        action_group.add_action_with_accel(self.action_edit_find_prev, "<Shift>F3")
        
        self.action_toggle_toc = Gtk.Action("ViewTOC", "_ToggleTOC",
            "Toggle the Table Of Contents", None)
        self.action_toggle_toc.connect("activate", self.on_toggle_toc)
        action_group.add_action_with_accel(self.action_toggle_toc, "<Ctrl>t")
        self.action_toggle_toc.set_sensitive(False)
        
        
        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(UI_INFO)
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)
        
        uimanager.insert_action_group(action_group)
        
        box = Gtk.Box()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        menubar = uimanager.get_widget("/MenuBar")
        #toolbar = uimanager.get_widget("/ToolBar")
        #toolbar.set_orientation(Gtk.Orientation.VERTICAL)
        self.findbar = Gtk.Toolbar()
        self.findbar.set_style(Gtk.ToolbarStyle.ICONS)
        
        vbox.pack_start(menubar, False, False, 0)
        #box.pack_start(toolbar, False, False, 0)
        vbox.pack_start(self.findbar, False, False, 0)
        vbox.pack_start(box, True, True, 0)

        self.search_box = Gtk.Entry()
        self.search_box.connect("activate", self.on_find_next)
        self.search_box.connect("key-press-event", self.on_search_box_key_press)
        search_box_wrapper = Gtk.ToolItem()
        search_box_wrapper.add(self.search_box)
        self.findbar.insert(search_box_wrapper, 0)
        
        self.find_next_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_DOWN)
        self.find_next_btn.connect("clicked", self.on_find_next)
        self.findbar.insert(self.find_next_btn, 1)
        
        self.find_prev_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_UP)
        self.find_prev_btn.connect("clicked", self.on_find_prev)
        self.findbar.insert(self.find_prev_btn, 2)
        
        expander = Gtk.ToolItem()
        expander.set_expand(True)
        self.findbar.insert(expander, 3)
        
        self.findbar_close_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_CLOSE)
        self.findbar_close_btn.connect("clicked", self.on_findbar_close)
        self.findbar.insert(self.findbar_close_btn, 4)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        self.webView = WebKit.WebView()
        scrolledwindow.add(self.webView)
        box.pack_start(scrolledwindow, True, True, 0)
        
        # Disable the default right-click menu:
        settings = self.webView.get_settings()
        settings.set_property('enable-default-context-menu', False)
        self.webView.set_settings(settings)
        
        self.webView.connect('navigation-requested', self.on_nav_req)
        
        
        self.window.add(vbox)
        self.window.connect("delete-event", Gtk.main_quit)
        
        self.window.show_all()
        
        self.findbar.set_visible(False)
        
    def on_nav_req(self, view, frame, request):
        if request != None:
            current_file_uri = FILE_PROTO+urllib.pathname2url(self.last_loaded_file).replace("%7E", "~")
            uri = request.get_uri()
            if uri.startswith(current_file_uri):
                 return WebKit.NavigationResponse.ACCEPT
            else:
                self.load_uri_in_system_browser(uri)
                return WebKit.NavigationResponse.IGNORE
        
    def load_uri_in_system_browser(self, uri):
        if PLATFORM == "windows":
           os.system("start "+uri) 
        else:
            subprocess.Popen("xdg-open "+uri, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    
    def on_findbar_close(self, widget):
        self.findbar.set_visible(False)

    def on_search_box_key_press(self, widget, key):
        if key.keyval == Gdk.KEY_Escape :
            self.on_findbar_close(widget)
        return False

    def on_find(self, widget):
        c = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        selected_text = c.wait_for_text()
        self.findbar.set_visible(True)
        self.search_box.grab_focus()
        if selected_text != None and selected_text != "":
            self.search_box.set_text(selected_text)

    def on_find_next(self, widget):
        self.search_text(self.search_box.get_text().strip(), True)
        
    def on_find_prev(self, widget):
        self.search_text(self.search_box.get_text().strip(), False)

    def search_text(self, text, forward_search):
        if (text != None) and (text != "") :
            self.webView.search_text(text, False, forward_search, True)

    def get_js_includes(self, fpath):
        result = ""
        parent_dir = os.path.split(fpath)[0]
        for f in sorted(os.listdir(parent_dir)):
            if f.endswith(".js"):
                bname = os.path.basename(f)
                result = result + "    <script src='"+os.path.basename(f)+"'></script>\n"
        return result

    def get_css_includes(self, fpath):
        result = ""
        parent_dir = os.path.split(fpath)[0]
        for f in sorted(os.listdir(parent_dir)):
            if f.endswith(".css"):
                bname = os.path.basename(f)
                if bname != "style.css":
                    result = result + "    <link rel='stylesheet' type='text/css' href='"+bname+"' />\n"
        return result

    def run(self):
        Gtk.main()
        
    def on_quit(self, widget):
        Gtk.main_quit()
        
    def on_load_file(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        
        fpath = dialog.get_filename()
        
        dialog.destroy()
        
        
        if response == Gtk.ResponseType.OK:
            ext = os.path.splitext(fpath)[1]
            ext = ext.lower()
            if ext == '.mdz':
                self.load_zipped(fpath)
            else:
                self.load_file(fpath)
            

    def rmdir(self):
		print "rm_tmp_dir"
		if self.doc_dir != None:
			try:
				shutil.rmtree(self.doc_dir)  # delete directory
			except OSError as exc:
				pass
	
    def load_zipped(self, file_path):
        self.rmdir()
        self.doc_dir = tempfile.mkdtemp()
        dest_dir = self.doc_dir
        fname =  os.path.splitext(os.path.basename(file_path))[0]
        zf = zipfile.ZipFile(file_path)
        zf.extractall(path=dest_dir)
        self.load_file(os.path.join(dest_dir, fname+".md"))

    def add_filters(self, dialog):
        filter_markdown = Gtk.FileFilter()
        filter_markdown.set_name("Markdown files")
        filter_markdown.add_pattern("*.md")
        filter_markdown.add_mime_type("text/x-markdown")
        dialog.add_filter(filter_markdown)
        
        
        filter_markdown_zipped = Gtk.FileFilter()
        filter_markdown_zipped.set_name("Zipped Markdown files")
        filter_markdown_zipped.add_pattern("*.mdz")
        dialog.add_filter(filter_markdown_zipped)

    def load_file(self, file_path):
    
        input_file = codecs.open(file_path, mode="r", encoding="utf-8")
        text = input_file.read()
        html = HTML_PRE + self.get_css_includes(file_path) + HTML_STYLE + self.get_js_includes(file_path) + HTML_MID + markdown.markdown(text, output_format="html5", extensions=['headerid','codehilite(css_class=code,guess_lang=True)', 'extra']) + HTML_POST
        f = open("test.html", "w")
        f.write(html)
        f.close()
        self.last_loaded_file = file_path
        self.webView.load_html_string(html, FILE_PROTO+urllib.pathname2url(file_path).replace("%7E", "~"))
        self.window.set_title(os.path.basename(file_path))
        self.action_reload.set_sensitive(True)
        self.action_toggle_toc.set_sensitive(True)
        
    def on_reload_file(self, widget):
        if self.last_loaded_file != None:
            self.load_file(self.last_loaded_file)
            
    def on_toggle_toc(self, widget):
        self.webView.execute_script("""
        $('#markdown_content').toggleClass('with_offset_for_toc');
        $('#toc').animate({width: 'toggle'}, {
            progress: function(animation, progress, remainingMs){
                $('#markdown_content').attr('margin-left', $('#toc').width()+"px");
            }
        }); 
        """);

viewer = MarkdownViewer()
viewer.run()
#viewer.rm_tmp_dir()

