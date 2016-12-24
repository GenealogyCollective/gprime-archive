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
plg.id    = 'im_ged'
plg.name  = _('GEDCOM')
plg.description =  _('GEDCOM is used to transfer data between genealogy programs. '
                'Most genealogy software will accept a GEDCOM file as input.')
plg.version = '1.0'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'importgedcom.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "ged"

#------------------------------------------------------------------------
#
# Gramps package (portable XML)
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_gpkg'
plg.name  = _('Gramps package (portable XML)')
plg.description =  _('Import data from a Gramps package (an archived XML '
                     'Family Tree together with the media object files.)')
plg.version = '1.0'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'importgpkg.py'
plg.ptype = IMPORT
plg.import_function = 'impData'
plg.extension = "gpkg"

#------------------------------------------------------------------------
#
# Gramps XML database
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'im_gramps'
plg.name  = _('Gramps XML Family Tree')
plg.description =  _('The Gramps XML format is a text '
                     'version of a Family Tree. It is '
                     'read-write compatible with the '
                     'present Gramps database format.')
plg.version = '1.0'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'importxml.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "gramps"

#------------------------------------------------------------------------
#
# JSON
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'JSON Import'
plg.name  = _('JSON Import')
plg.description =  _('This is a JSON import')
plg.version = '1.0.6'
plg.gprime_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'JSONImport.py'
plg.ptype = IMPORT
plg.import_function = 'importData'
plg.extension = "json"
