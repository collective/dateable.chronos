# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: day.py 47783 2006-08-02 11:34:03Z lregebro $ """ day.py """

from datetime import timedelta, date

from zope.interface import implements
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

#from AccessControl import getSecurityManager

from displaytable import DayGrid
from interfaces import IPositionedView, IEventDisplay

from base_view import BaseCalendarView

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

# Some defaults for rendering:
CALENDAR_WIDTH = 738

class DayView(BaseCalendarView):
    """Holds the rendering information for day views"""

    implements(IPositionedView)

    def __getitem__(self, key):
        return self.index.macros[key]

    def calcInfo(self):
        self.today = self._get_default_day()
        self.day = self.today.day
        self.month = self.today.month
        self.year = self.today.year

        self.first_day = self.column_day = date(self.year, self.month, self.day)
        self.week = self.first_day.isocalendar()[1]
        self.days = 1

        p_cal = getToolByName(self.context, 'portal_calendar')
        self.from_hour = p_cal.hour_start
        self.to_hour = p_cal.hour_end

        self.hour_count = self.to_hour - self.from_hour

        # We might want to make this more flexible for different layouts
        # The 650 pixel width is good for the default CPS design on my
        # screen. Not very generic.
        self.day_width = self.width = CALENDAR_WIDTH
        self.hour_height = p_cal.getDayHourHeight()
        self.height = self.hour_height * self.hour_count
        # Add on the "before" and "after" lines.
        self.before_line = False
        self.after_line = False
        if self.from_hour > 0:
            self.height = self.height  + self.hour_height
            self.before_line = True
        if self.to_hour < 23:
            self.height = self.height  + self.hour_height
            self.after_line = True

    def getDate(self):
        return self.first_day

    def getDays(self):
        return [self.getDate()]

    def getEventDisplays(self):
        """ gathers event-like objects from an event provider """
        occurrences = self.getOccurrencesInDay(self.today)
        displays = [getMultiAdapter([occurrence, self], IEventDisplay)
                  for occurrence in occurrences]

        # Handle overlapping displays:
        daygrid = DayGrid(0, 0, self.height, self.day_width)
        daygrid.extend(displays)
        daygrid.flatten()

        return daygrid

    def getTodayInfo(self):
        today = date.today()
        if today == self.first_day:
            istoday = True
        else:
            istoday = False
        return {'year': today.year,
                'month': today.month,
                'day': today.day,
                'istoday': istoday}

    def getPreviousViewUrl(self):
        return self.getDateUrl(self.default_day - timedelta(days=1), 'day')

    def getNextViewUrl(self):
        return self.getDateUrl(self.default_day + timedelta(days=1), 'day')

    def getTodayUrl(self):
        return self.context.absolute_url() + '/day.html?date='
