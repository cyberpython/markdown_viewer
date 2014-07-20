#*
#*  The MIT License
#*
#*  Copyright 2014 Georgios Migdos <cyberpython@gmail.com>
#*
#*  Permission is hereby granted, free of charge, to any person obtaining a copy
#*  of this software and associated documentation files (the "Software"), to deal
#*  in the Software without restriction, including without limitation the rights
#*  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#*  copies of the Software, and to permit persons to whom the Software is
#*  furnished to do so, subject to the following conditions:
#*
#*  The above copyright notice and this permission notice shall be included in
#*  all copies or substantial portions of the Software.
#*
#*  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#*  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#*  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#*  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#*  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#*  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#*  THE SOFTWARE.
#*
all:
	
clean:
	
distclean:
	
uninstall: 
	rm -f $(DESTDIR)/usr/share/applications/markdown_viewer.desktop
	rm -f $(DESTDIR)/usr/share/icons/hicolor/scalable/apps/markdown_viewer.svg
	rm -f $(DESTDIR)/usr/bin/markdown_viewer
	rm -rf $(DESTDIR)/usr/share/markdown_viewer
	
	
install:
	mkdir -p $(DESTDIR)/usr/bin/
	mkdir -p $(DESTDIR)/usr/share/markdown_viewer
	mkdir -p $(DESTDIR)/usr/share/icons/hicolor/scalable/apps
	mkdir -p $(DESTDIR)/usr/share/applications
	cp css/style.css $(DESTDIR)/usr/share/markdown_viewer/style.css
	cp css/toc.css $(DESTDIR)/usr/share/markdown_viewer/toc.css
	cp js/jquery.js $(DESTDIR)/usr/share/markdown_viewer/jquery.js
	cp js/toc.js $(DESTDIR)/usr/share/markdown_viewer/toc.js
	cp js/markdown_viewer.js $(DESTDIR)/usr/share/markdown_viewer/markdown_viewer.js
	cp markdown_viewer $(DESTDIR)/usr/bin/markdown_viewer
	cp markdown_viewer.svg $(DESTDIR)/usr/share/icons/hicolor/scalable/apps/markdown_viewer.svg
	cp markdown_viewer.desktop $(DESTDIR)/usr/share/applications/markdown_viewer.desktop
	chmod ugo+x $(DESTDIR)/usr/bin/markdown_viewer
	
