Description
-----------

Simple python + GTK3 based Markdown viewer.

The application can also open 'Compressed Markdown Files', which are regular ZIP 
archives with the extension '.mdz' that contain a markdown file in their root
 named with the same name as the ZIP archive. 
 
For example the archive named 'test.mdz' should contain a Markdown file named
'test.md' in its root along with any other files (e.g. images) the Markdown file 
references (each placed in the correct relative path).

The generated HTML document will try to load the following CSS files:

- file:///usr/share/markdown_viewer/style.css
- all '.css' files in the same directory with the Markdown file except 'style.css' 
  in ascending alphabetical order
- style.css

The bundled JQuery, TOC.js and markdown_viewer.js  are the first scripts that are loaded.

The generated HTML5 document will try to load any '.js' files in the same 
directory with the Markdown file in ascending alphabetical order.


Highlighted code by the codehilite extension is assigned the '.code' CCS class.

* python-markdown is used for parsing.
* WebKit 3 is used for rendering.
* jQuery and TOC.js are used to display the table of contents.
* The application's icon is a derivative of the devhelp icon from the [Gnome-icons project](https://github.com/gnome-design-team/gnome-icons) available under the Creative Commons Attribution-Share Alike 3.0 license.

Requirements
------------

* Python 2.7+ (not Python 3+)
* GTK 3.x
* PyGI
* python-markdown
* WebKit 3 for GTK

