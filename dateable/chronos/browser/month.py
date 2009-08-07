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
# $Id: month.py 48535 2006-08-23 18:15:50Z lregebro $
"""
  month.py
"""

import calendar
from datetime import date, timedelta
from zope.component import getMultiAdapter
from zope.interface import implements

from interfaces import IUnPositionedView, IEventDisplay
from base_view import BaseCalendarView

def cmp_occurrence(a, b):
    return cmp(a.start, b.start)

class MonthView(BaseCalendarView):
    """Holds the rendering information for month views"""

    implements(IUnPositionedView)

    def calcInfo(self):
        """Calculates all the information necessary for display"""
        self.calendar = self.context
        self.year = int(self.year())
        self.month = self.default_day.month

        # store the start date of the month
        self.monthstart = date(self.year, self.month, 1)
        # calculate the start date of the next month
        if self.month == 12:
            self.nextmonth = date(self.year+1, 1, 1)
        else:
            self.nextmonth = date(self.year, self.month +1, 1)
        
        # first monday to be displayed
        self.begins = self.monthstart - timedelta(self.monthstart.weekday())
        # last sunday to be displayed
        self.ends = self.nextmonth + timedelta(6 - self.nextmonth.weekday())
        # amount of weeks to display
        self.weeks = int(((self.ends - self.begins).days + 1) / 7)

        self.first_week = self.begins.isocalendar()[1]

        # A per viewing cache of which days that have more events than can
        # be displayed, just to avoid searching each day twice.
        self.date_display_maxed = {}
            
    def getDateForWeekDay(self, week, weekday=None):
        # week is number of week in view, ie 0 to 5.
        # weekday is 1 to 7
        if weekday is None:
            # Use the weekday of the currently used date
            weekday = self.default_day.weekday() + 1
        # Calculate:
        return self.begins + timedelta(week * 7 + weekday - 1)

    def getOccurrenceDisplays(self, day):
        occurrences =  self.getOccurrencesInDay(day)
        occurrences.sort(cmp=cmp_occurrence)
        count = 0
        self.date_display_maxed[day] = 0
        displays = []
        for occurrence in occurrences:
            count += 1
            if self.calendar_tool.iseventsdisplaylimited and \
                count > self.calendar_tool.displaymaxevents:
                self.date_display_maxed[day] = 1
                break
            displays.append(getMultiAdapter([occurrence, self], IEventDisplay))
        # Cut off the last one (to be replaced by a More... tag)
        if self.date_display_maxed[day] == 1:
            displays = displays[:-1]
        return displays
    
    def hasMoreEvents(self, day):
        """Returns true if there are more events than can be displayed"""
        if not self.date_display_maxed.has_key(day):
            # We haven't checked yet:
            self.getOccurrenceDisplays(day)            
        return self.date_display_maxed[day]

    def getTodayInfo(self):
        today = date.today()
        if today.year == self.year and today.month == self.month:
            istoday = True
        else:
            istoday = False
        return {'year': today.year, 
                'month': today.month, 
                'day': today.day,
                'istoday': istoday}
    
    def getClassForDate(self, dt):
        if dt.month == self.context.getMonth():
            class_ = 'thisMonth'
        else:
            class_ = 'otherMonth'
        if len(self.calendar.getOccurrencesInDay(dt)) != 0:
            class_ += 'HasEvent'
        else:
            class_ += 'NoEvent'
        return class_

    def _get_view_url_for_date(self, year, month, day):
        weekday, days_in_month = calendar.monthrange(year, month)
        if days_in_month < day:
            day = days_in_month
        return self.getDateUrl(date(year, month, day), 'month')

    def getPreviousViewUrl(self):
        year = self.default_day.year
        month = self.default_day.month
        day = self.default_day.day
        if month == 1:
            year, month = year-1, 12
        else:
            month -= 1
        return self._get_view_url_for_date(year, month, day)

    def getNextViewUrl(self):
        year = self.default_day.year
        month = self.default_day.month
        day = self.default_day.day
        if month == 12:
            year, month = year+1, 1
        else:
            month += 1
        return self._get_view_url_for_date(year, month, day)

    def getTodayUrl(self):
        return self.context.absolute_url() + '/month.html?date='
