For developers:

## Editing Templates

When editing the templates in `gprime/share/gprime/data/templates/*.html`, you may use:

* `{{_("Text")}}` - replaces whole expression with translated text
* `{{_T_("Test")}}` - replaces whole expression with translated text, in quotes

## Generation

In gprime/po run the command `./genpot.sh`. That will go through all source and templates and update the `gprime.po` file.
