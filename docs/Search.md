# Search

On each list view of each object type (e.g., Person, Family, etc) there is a search field. The search field allows entering search criteria for matching all possible values.

All matching is case-insensitive.

## General Search

If you enter a simple phrase, such as `Elizabeth` then all of the default fields will be searched on that table. For example, on the Person view, gPrime would search surname and given.

### Wildcards

You may use the wildcard symbol `%` to match any characters. For example, `Bl%nk` would match:

* Blank
* Blenk
* Blightplank

That is, `Bl%nk` would match any default field that starts with a `Bl` and ends with an `nk`.

## Specific Search

If you specify which field to search, then gPrime will search exactly. The search `given=Elizabeth` will only match that data that has exactly `Elizabeth` as a given name. You can use the wildcard to match middle names, e.g. `given=Elizabeth%`.

## Multiple criteria

You may use commas to separate AND criteria. You may use | to separate OR criteria. OR has higher precedence than AND. 

[gPrime Schema](http://htmlpreview.github.io/?https://github.com/GenealogyCollective/gprime/blob/master/docs/Schema.html)

## Examples

