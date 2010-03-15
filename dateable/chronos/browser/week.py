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
# $Id: week.py 47783 2006-08-02 11:34:03Z lregebro $
"""
  week.py
"""

from datetime import timedelta, date
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from dateable.chronos import isoweek
from base_view import BaseCalendarView
from displaytable import DayGrid
from interfaces import IPositionedView, IEventDisplay

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

# Some defaults for rendering:
HOUR_HEIGHT = 30 # Two minutes per pixel
CALENDAR_WIDTH = 738

class WeekView(BaseCalendarView):
    """Holds the rendering information for week views"""
    
    implements(IPositionedView)

    def prev_long_link(self):
        return self.prev_month_link()

    def prev_short_link(self):
        return self.prev_week_link()

    def next_short_link(self):
        return self.next_week_link()

    def next_long_link(self):
        return self.next_month_link()

    def getWeekdays(self):
        return range(1, 8)

    def getDateForWeekday(self, weekday):
        return isoweek.weeknr2datetime(self.year, self.week, weekday)
    
    def calcInfo(self):
        self.calendar = self.context
        self.week = self.week()
        self.year = int(self.year())
        self.first_day = self.column_day = self.getDateForWeekday(1)
        self.month = self.first_day.month
        # self.ends is the day after the last day
        self.ends = self.first_day + timedelta(8)
        self.days = 7 

        p_cal = getToolByName(self.context, 'portal_calendar')
        self.from_hour = p_cal.hour_start
        self.to_hour = p_cal.hour_end
        self.hour_count = self.to_hour - self.from_hour

        # We might want to make this more flexible for different layouts
        # The 650 pixel width is good for the default CPS design on my
        # screen. Not very generic.
        self.day_width = CALENDAR_WIDTH / self.days
        # Make sure they match even if calendar_width isn't a multiple of 7
        self.width = self.day_width * self.days

        self.hour_height = HOUR_HEIGHT
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

    def getDays(self):
        return [self.getDateForWeekday(d) 
                for d in self.getWeekdays()]
            
    def getEventDisplays(self):
        all_displays = []
        for d in self.getWeekdays():
            day = self.getDateForWeekday(d)
            self.column_day = day
            occurrences = self.getOccurrencesInDay(day)
            displays = [getMultiAdapter([occurrence, self], IEventDisplay) for
                        occurrence in occurrences]
            
            # Handle overlapping displays:
            daygrid = DayGrid(0, self.day_width * (d-1), 
                                 self.height,
                                 self.day_width)
            daygrid.extend(displays)
            daygrid.flatten()
            all_displays.extend(daygrid)
            
        return all_displays

    def getTodayInfo(self):
        today = date.today()
        if (today >= self.first_day.date() and 
            today < (self.first_day + timedelta(7)).date()):
            istoday = True
        else:
            istoday = False
        return {'year': today.year, 
                'month': today.month, 
                'day': today.day,
                'istoday': istoday}
 
    def getPreviousViewUrl(self):
        return self.getDateUrl(self.default_day - timedelta(days=7), 'week')

    def getNextViewUrl(self):
        return self.getDateUrl(self.default_day + timedelta(days=7), 'week')
    
    def getTodayUrl(self):
        return self.context.absolute_url() + '/week.html?date='
