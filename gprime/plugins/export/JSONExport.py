# gPrime - a web-based genealogy program
#
# Copyright (C) 2013-2016  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2016       Nick Hall
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import json

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gprime.plug.utils import OpenFileOrStdout
from gprime.lib import (Note, Person, Event, Family, Repository, Place,
                        Media, Source, Tag, Citation)

def exportData(db, filename,
               error_dialog=None, option_box=None, callback=None):
    if not callable(callback):
        callback = lambda percent: None # dummy

    with OpenFileOrStdout(filename, encoding="utf-8") as fp:

        total = (db.get_number_of_notes() +
                 db.get_number_of_people() +
                 db.get_number_of_events() +
                 db.get_number_of_families() +
                 db.get_number_of_repositories() +
                 db.get_number_of_places() +
                 db.get_number_of_media() +
                 db.get_number_of_citations() +
                 db.get_number_of_sources() +
                 db.get_number_of_tags())
        count = 0.0

        # ---------------------------------
        # Notes
        # ---------------------------------
        for obj in db.iter_notes(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Event
        # ---------------------------------
        for obj in db.iter_events(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Person
        # ---------------------------------
        for obj in db.iter_people(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Family
        # ---------------------------------
        for obj in db.iter_families(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Repository
        # ---------------------------------
        for obj in db.iter_repositories(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Place
        # ---------------------------------
        for obj in db.iter_places(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Source
        # ---------------------------------
        for obj in db.iter_sources(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Citation
        # ---------------------------------
        for obj in db.iter_citations(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Media
        # ---------------------------------
        for obj in db.iter_media(order_by=[("gid", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Tag
        # ---------------------------------
        for obj in db.iter_tags(order_by=[("name", "ASC")]):
            write_line(fp, obj)
            count += 1
            callback(100 * count/total)

    return True

def write_line(fp, obj):
    """
    Write a single object to the file.
    """
    fp.write(json.dumps(obj.to_struct(), sort_keys=True) + "\n")
