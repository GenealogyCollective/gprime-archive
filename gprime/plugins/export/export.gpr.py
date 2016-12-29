#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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

MODULE_VERSION="1.0"

#------------------------------------------------------------------------
#
# GEDCOM
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'ex_ged'
plg.name  = _('GEDCOM')
plg.name_accell  = _('GE_DCOM')
plg.description =  _('GEDCOM is used to transfer data between genealogy programs. '
                'Most genealogy software will accept a GEDCOM file as input.')
plg.version = '1.0'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'exportgedcom.py'
plg.ptype = EXPORT
plg.export_function = 'export_data'
plg.export_options = 'WriterOptionBox'
plg.export_options_title = _('GEDCOM export options')
plg.extension = "ged"

#------------------------------------------------------------------------
#
# Gramps package (portable XML)
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'ex_gpkg'
plg.name  = _('Gramps XML Package (family tree and media)')
plg.name_accell  = _('Gra_mps XML Package (family tree and media)')
plg.description =  _('Gramps package is an archived XML family tree together '
                 'with the media object files.')
plg.version = '1.0'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'exportpkg.py'
plg.ptype = EXPORT
plg.export_function = 'writeData'
plg.export_options = 'WriterOptionBox'
plg.export_options_title = _('Gramps package export options')
plg.extension = "gpkg"

#------------------------------------------------------------------------
#
# Gramps XML database
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'ex_gramps'
plg.name  = _('Gramps XML (family tree)')
plg.name_accell  = _('Gramps _XML (family tree)')
plg.description =  _('Gramps XML export is a complete archived XML backup of a'
                 ' Gramps family tree without the media object files.'
                 ' Suitable for backup purposes.')
plg.version = '1.0'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'exportxml.py'
plg.ptype = EXPORT
plg.export_function = 'export_data'
plg.export_options = 'WriterOptionBoxWithCompression'
plg.export_options_title = _('Gramps XML export options')
plg.extension = "gramps"

#------------------------------------------------------------------------
#
# JSON
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'JSON Export'
plg.name  = _('JSON Export')
plg.description =  _('This is a JSON export')
plg.version = '1.0.6'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'JSONExport.py'
plg.ptype = EXPORT
plg.export_function = 'exportData'
plg.export_options = 'WriterOptionBox'
plg.export_options_title = _('JSON options')
plg.extension = "json"

