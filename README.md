Gprime [![Build Status](https://travis-ci.org/GenealogyCollective/gprime.svg?branch=master)](https://travis-ci.org/GenealogyCollective/gprime)[![codecov.io](https://codecov.io/github/GenealogyCollective/gprime/coverage.svg?branch=master)](https://codecov.io/github/GenealogyCollective/gprime?branch=master)
===================
We strive to produce a genealogy program that is both intuitive for hobbyists and feature-complete for professional genealogists.

Requirements
============
The following packages are required:

* **Python** 3.2 or greater - The programming language used by Gprime. https://www.python.org/
* **GTK** 3.10 or greater - A cross-platform widget toolkit for creating graphical user interfaces. http://www.gtk.org/
* **pygobject** 3.12 or greater - Python Bindings for GLib/GObject/GIO/GTK+ https://wiki.gnome.org/Projects/PyGObject

The following three packages with GObject Introspection bindings (the gi packages)

* **cairo** - a 2D graphics library with support for multiple output devices. http://cairographics.org/
* **pango** - a library for laying out and rendering of text, with an emphasis on internationalization. http://www.pango.org/
* **pangocairo** - Allows you to use Pango with Cairo http://www.pango.org/

* **librsvg2** - (SVG icon view) a library to render SVG files using cairo. http://live.gnome.org/LibRsvg
* **xdg-utils** - Desktop integration utilities from freedesktop.org
* **bsddb3** - Python bindings for Oracle Berkeley DB https://pypi.python.org/pypi/bsddb3/
* **Meta** - Ability to define quick access to databases

The following package is needed for full translation of the interface
to your language:

*   **language-pack-gnome-xx**

 Translation of GTK elements to your language, with
 xx your language code; e.g. for Dutch you need
 language-pack-gnome-nl. The translation of the

The following packages are recommended:
--------------------------------------------------------------------
*  **osmgpsmap**

 Used to show maps in the geography view.
 It may be osmgpsmap, osm-gps-map, or python-osmgpsmap,
 but the Python bindings for this must also be present.
 Without this the GeoView will not be active, see

* **Graphviz**

  Enable creation of graphs using Graphviz engine.
  Without this, three reports cannot be run.
  Obtain it from: http://www.graphviz.org

* **PyICU**

 Improves localised sorting in Gprime. In particular, this
 applies to sorting in the various views and in the
 Narrative Web output. It is particularly helpful for
 non-Latin characters, for non-English locales and on MS
 Windows and Mac OS X platforms. If it is not available,
 sorting is done through built-in libraries. PyICU is
 fairly widely available through the package managers of
 distributions. See http://pyicu.osafoundation.org/
 (These are Python bindings for the ICU package. 
 https://pypi.python.org/pypi/PyICU/)

The following packages are optional:
------------------------------------
* **gtkspell** 

 Enable spell checking in the notes. Gtkspell depends on
 enchant. A version of gtkspell with gobject introspection
 is needed, so minimally version 3.0.0

* **PIL**

 Python Image Library is needed to crop
 images and also to convert non-JPG images to
 JPG so as to include them in LaTeX output.
 (For Python3 a different source may be needed,
 python-imaging or python-pillow or python3-pillow)

* **GExiv2**

 Enables Gprime to manage Exif metadata embedded in your
 media. Gprime needs version 0.5 or greater.

* **ttf-freefont**

 More font support in the reports

Documentation
-------------
The User Manual is under development.

