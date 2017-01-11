#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2015 Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Gramps imports:
from gprime.lib.note import Note
from gprime.plugins.docgen.htmldoc import HtmlDoc
from gprime.plugins.lib.libhtmlbackend import HtmlBackend, DocBackend, process_spaces
from gprime.plugins.lib.libhtml import Html
from gprime.lib import StyledText, StyledTextTag
from gprime.db import DbTxn

# Gramps Connect imports:
from .forms import Form

# Python:
from html.parser import HTMLParser

class NoteForm(Form):
    """
    A form for listing, viewing, and editing a Person object.
    """
    _class = Note
    view = "note"
    tview = "Note"
    table = "Note"

    # Fields for editor:
    edit_fields = [
        "type",
        "gid",
        "tag_list",
        "private",
        "format",
    ]

    # URL for page view rows:
    link = "/note/%(handle)s"

    # Search fields to use if not specified:
    default_search_fields = [
        "text.string",
        "gid",
    ]

    # Search fields, list is OR
    search_terms = {
        "text": "text.string",
        "id": "gid",
    }

    order_by = [("gid", "ASC")]

    # Fields for page view; width sum = 95%:
    select_fields = [
        ("gid", 10),
        ("text.string", 85),
    ]

    # Other fields needed to select:
    env_fields = [
        "handle",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snf = StyledNoteFormatter(self)

    def render_note(self, user, action):
        # note to html:
        notetext = self.snf.format(self.instance)
        if action == "edit":
            return """<textarea rows="10" cols="80" class="wysiwyg">%s</textarea>""" % notetext
        else:
            return """<div id="" style="overflow-y:scroll; height:180px; background-color:white">%s</div>""" % notetext

    def load_data(self):
        super().load_data()
        text = self.handler.get_argument("notetext")
        parser = WebAppParser(self)
        text = text.replace("&nbsp;", " ") # otherwise removes them?
        parser.feed(text)
        parser.close()
        self.instance.text = StyledText(
            parser.text(),
            [StyledTextTag(*args) for args in parser.tags()])

class WebAppBackend(HtmlBackend):
    SUPPORTED_MARKUP = [
            DocBackend.BOLD,
            DocBackend.ITALIC,
            DocBackend.UNDERLINE,
            DocBackend.FONTFACE,
            DocBackend.FONTSIZE,
            DocBackend.FONTCOLOR,
            DocBackend.HIGHLIGHT,
            DocBackend.SUPERSCRIPT,
            DocBackend.LINK,
            ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        : ("<b>", "</b>"),
        DocBackend.ITALIC      : ("<i>", "</i>"),
        DocBackend.UNDERLINE   : ('<u>', '</u>'),
        DocBackend.SUPERSCRIPT : ("<sup>", "</sup>"),
    }

### Taken from Narrated Web Report
class StyledNoteFormatter(object):
    def __init__(self, form):
        self.form = form
        self.database = form.database
        self._backend = WebAppBackend()
        self._backend.build_link = self.build_link

    def format(self, note):
        return self.styled_note(note.get_styledtext())

    def styled_note(self, styledtext):
        text = str(styledtext)
        if not text:
            return ''
        s_tags = styledtext.get_tags()
        markuptext = self._backend.add_markup_from_styled(text, s_tags, split='\n').replace("\n\n", "<p></p>").replace("\n", "<br/>")
        return markuptext

    def build_link(self, prop, handle, obj_class):
        """
        Build a link to an item.
        """
        if prop == "gramps_id":
            if obj_class in self.database.get_table_names():
                obj = self.database.get_table_metadata(obj_class)["gid_func"](handle)
                if obj:
                    handle = obj.handle
                else:
                    raise AttributeError("gramps_id '%s' not found in '%s'" %
                                         (handle, obj_class))
            else:
                raise AttributeError("invalid gramps_id lookup " +
                                     "in table name '%s'" % obj_class)
        # handle, ppl
        return self.form.handler.app.make_url("/%s/%s" % (obj_class.lower(), handle))

class WebAppParser(HTMLParser):
    BOLD = 0
    ITALIC = 1
    UNDERLINE = 2
    FONTFACE = 3
    FONTSIZE = 4
    FONTCOLOR = 5
    HIGHLIGHT = 6 # background color
    SUPERSCRIPT = 7
    LINK = 8

    def __init__(self, form):
        HTMLParser.__init__(self)
        self.form = form
        self.__text = ""
        self.__tags = {}
        self.__stack = []

    def handle_data(self, data):
        self.__text += data

    def push(self, pos, tag, attrs):
        self.__stack.append([pos, tag, attrs])

    def pop(self):
        return self.__stack.pop()

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.__text += "\n"
            return
        self.push(len(self.__text), tag.lower(), attrs)

    def handle_startstoptag(self, tag, attrs):
        if tag == "br":
            self.__text += "\n"
            return
        elif tag == "p":
            self.__text += "\n\n"
            return
        else:
            print("Unhandled start/stop tag '%s'" % tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ["br"]: return
        (start_pos, start_tag, attrs) = self.pop()
        attrs = dict(attrs)
        if tag != start_tag: return # skip <i><b></i></b> formats
        arg = None
        tagtype = None
        if tag == "span":
            # "span": get color, font, size
            if "style" in attrs:
                style = attrs["style"]
                if 'color' in style:
                    tagtype = self.FONTCOLOR
                    match = re.match("color:([^;]*);", style)
                    if match:
                        arg = match.groups()[0]
                    else:
                        print("Unhandled color tag: '%s'" % style)
                elif 'background-color' in style:
                    tagtype = self.HIGHLIGHT
                    match = re.match("background-color:([^;]*);", style)
                    if match:
                        arg = match.groups()[0]
                    else:
                        print("Unhandled background-color tag: '%s'" % style)
                elif "font-family" in style:
                    tagtype = self.FONTFACE
                    match = re.match("font-family:'([^;]*)';", style)
                    if match:
                        arg = match.groups()[0]
                    else:
                        print("Unhandled font-family tag: '%s'" % style)
                elif "font-size" in style:
                    tagtype = self.FONTSIZE
                    match = re.match("font-size:([^;]*)px;", style)
                    if match:
                        arg = int(match.groups()[0])
                    else:
                        print("Unhandled font-size tag: '%s'" % style)
                else:
                    print("Unhandled span arg: '%s'" % attrs)
            else:
                print("span has no style: '%s'" % attrs)
        # "b", "i", "u", "sup": direct conversion
        elif tag == "b":
            tagtype = self.BOLD
        elif tag == "i":
            tagtype = self.ITALIC
        elif tag == "u":
            tagtype = self.UNDERLINE
        elif tag == "sup":
            tagtype = self.SUPERSCRIPT
        elif tag == "p":
            self.__text += "\n\n"
            return
        elif tag == "div":
            self.__text += "\n"
            return
        elif tag == "a":
            tagtype = self.LINK
            # "a": get /object/handle, or url
            if "href" in attrs:
                href = attrs["href"]
                if href.startswith(self.form.handler.app.make_url("/")):
                    # remove prefix:
                    href = href[len(self.form.handler.app.prefix):]
                    parts = href.split("/")
                    arg = "gramps://%s/handle/%s" % (parts[-2].title(), parts[-1])
                else:
                    arg = href
            else:
                print("Unhandled a with no href: '%s'" % attrs)
        else:
            return
            print("Unhandled tag: '%s'" % tag)

        if start_pos == len(self.__text): return # does nothing
        key = ((tagtype, ''), arg)
        if key not in self.__tags:
            self.__tags[key] = []
        self.__tags[key].append((start_pos, len(self.__text)))

    def tags(self):
        # [((code, ''), string/num, [(start, stop), ...]), ...]
        return [(key[0], key[1], self.__tags[key]) for key in self.__tags]

    def text(self):
        return self.__text

    def delete(self):
        note_handle = self.instance.handle
        with DbTxn(self._("Delete note"), self.database) as transaction:
            for (item, handle) in self.database.find_backlink_handles(note_handle):
                handle_func = self.database.get_table_func(item, "handle_func")
                commit_func = self.database.get_table_func(item, "commit_func")
                obj = handle_func(handle)
                obj.remove_handle_references('Note', [note_handle])
                commit_func(obj, transaction)
            self.database.remove_note(self.instance.handle, transaction)
        self.handler.send_message("Deleted note. <a href='FIXME'>Undo</a>.")
        self.handler.redirect(self.handler.app.make_url("/note"))
