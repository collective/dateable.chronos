# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""Occurrence rendering logic"""

from datetime import timedelta, datetime, time
from AccessControl import getSecurityManager

from zope.interface import implements
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

import dtutils

from displaytable import Cell
from interfaces import IEventDisplay


# XXX This is reused in several places by copy/paste.
# Some sort of refactoring here would be good.
def checkPermission(permission, object):
    user = getSecurityManager().getUser()
    return user.has_permission(permission, object)


class EventDisplay(Cell):
    """Adapts en event to IEventDisplay
    """

    implements(IEventDisplay)

    def __init__(self, event, view):
        """Creates and calculates render information"""

        self.event = event
        self.view = view

        # XXX Check permissions
        self.viewable = True
        # TODO: Here we could calculate short titles that fit into one row
        # and how much of the decription fits and stuff like that as well.
        if self.viewable:
            self.title = event.title
            self.description = event.description
            self.url = event.url
        else:
            self.title = self.description = _('Private Event')
            self.url = ''

        event_begins = event.start
        event_ends = event.end
        self.title_and_time = "%s %02d:%02d - %02d:%02d" % (self.title,
                                        event_begins.hour,event_begins.minute,
                                        event_ends.hour, event_ends.minute)


class PositionedEventDisplay(EventDisplay):

    implements(IEventDisplay)

    def __init__(self, event, view):
        """Creates and calculates render information, like dimensions etc.

        View must be a IPositionedView.
        """
        EventDisplay.__init__(self, event, view)

        # Get the local timezone
        self.tz = dtutils.gettz()

        event_begins = event.start
        event_ends = event.end
        column_day = view.column_day

        first_day = view.first_day
        if isinstance(first_day, datetime):
            first_day = first_day.date()

        if view.from_hour != 0:
            day_begins = datetime.combine(column_day, time(view.from_hour - 1))
        else:
            day_begins = datetime.combine(column_day, time(0))
        day_begins = day_begins.replace(tzinfo=self.tz)

        if view.to_hour != 24:
            if view.to_hour != 23:
                day_ends = datetime.combine(column_day, time(view.to_hour + 1))
            else:
                day_ends = datetime.combine(column_day, time(view.to_hour))
        else:
            day_ends = datetime.combine(column_day + timedelta(1),  time(0))
        day_ends = day_ends.replace(tzinfo=self.tz)

        start_delta = event_begins - day_begins
        if start_delta < timedelta(0):
            start_delta = timedelta(0)
        self.startpos = start_delta

        if event_ends > day_ends:
            self.endpos = day_ends - day_begins
            if self.startpos > self.endpos:
                self.startpos = self.endpos
        else:
            end_delta = event_ends - day_begins
            if end_delta < timedelta(hours=1):
               end_delta = timedelta(hours=1)
            self.endpos = end_delta

        # Now calculate the css-dimensions
        self.top = (self.startpos.seconds * view.hour_height) / 3600
        duration = self.endpos - self.startpos
        self.height = ((duration.seconds or duration.days * (3600 *24)) * view.hour_height) / 3600

        if self.height < 20:
            # Increase height, but not if we already hit the end of the day:
            max = (2 + view.to_hour - view.from_hour) * view.hour_height
            margin = max - self.top
            if margin < 20:
                self.top = self.top - (20 - margin)
            self.height = 20

        day = (event_begins.date() - first_day).days
        self.left = day * view.day_width
        self.width = view.day_width

        # Set Cell properties. These gets changed later when the Grid gets flatten()ed.
        Cell.__init__(self, self.top, 0, self.top + self.height, 1)

    def getCssPositionString(self):
        """Returns a properly formatted css-style position string.

        Usage in the template:
          tal:attributes="style event_render_info/getCssPositionString"
        """
        return "top:%spx;left:%0.1f%%;height:%spx;width:%.1f%%;"%(
            self.getFirstRow(),
            self.getFirstCol()*100.0/self.view.width,
            self.getLastRow() - self.getFirstRow(),
            (self.getLastCol() - self.getFirstCol())*100.0/self.view.width)

    def getCssStatusClass(self):
        """Returns a CSS class name according to the status of this event
        for the current user attendee (if there is one). Possible classes are:

            need-action
            accepted
            declined
            tentative
            delegated
            <empty>

        It is up to the actuall stylesheet to do something with this class.
        """
        return ''

    def getCssEventClass(self):
        """Returns the type of event for CSS selection

        Possible types are:
            public
            private
            confidential
            meeting
            unauthorized
        """
        if not self.viewable:
            return 'unauthorized'
        return self.event.access.lower()
