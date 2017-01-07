from gprime.lib import *
from gprime.lib.handle import HandleClass

def primary():
    return [Person, Event, Repository, Place, Citation,
            Source, Tag, Note, Family, Media]

def describe(item, indent=0, path=""):
    if isinstance(item, list):
        return "list of %s" % ", ".join(describe(i, indent + 4, path) for i in item)
    elif isinstance(item, tuple):
        return "tuple of %s" % ", ".join(describe(i, indent + 4, path) for i in item)
    elif item == int:
        return "integer"
    elif item == bool:
        return "boolean"
    elif item == str:
        return "string"
    elif isinstance(item, HandleClass):
        return "<a href=\"#%s\">%s</a>" % (item.classname, item.classname)
    elif hasattr(item, "get_schema"):
        schema = item.get_schema()
        fields = sorted(schema.keys())
        retval = " " * indent + "<ul>\n"
        for field in fields:
            if field in ["handle", "_class"]: # don't show these
                continue
            retval += (" " * (indent + 4)) + "<li><b>%s.%s</b>: %s</li>\n" % (path, field, describe(schema[field], indent + 4, path + "." + field))
        retval += " " * indent + "</ul>\n"
        if item in primary():
            return "<a id=\"%s\"><h2><li>%s</li></h2></a> [<a href=\"#top\">top</a>]\n%s" % (item.__name__, item.__name__, retval)
        else:
            return "<u>%s</u>:\n%s" % (item.__name__, retval)
    else:
        return "variable types"

print("<html>")
print("<body>")
print("<h1>gPrime Schema</h1>")
print("<p><a id=\"top\"></a>These are the primary objects in gPrime. Click on their names to see the full specification.</p>")
print("<ol>")
for table in primary():
    print("<li><a href=\"#%s\">%s</a></li>" % (table.__name__, table.__name__))
print("</ol>")
print("<hr/>")
print("<ol>")
for table in primary():
    print(describe(table, path=table.__name__))
print("</ol>")
print("</body>")
print("</html>")
