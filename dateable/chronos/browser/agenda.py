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
  agenda.py
"""

import calendar
from datetime import date, timedelta, time, datetime
from zope.component import getMultiAdapter
from zope.interface import implements

from interfaces import IUnPositionedView, IEventDisplay
from base_view import BaseCalendarView

from dateable import kalends

from dateable.chronos import isoweek
from base_view import BaseCalendarView
from displaytable import DayGrid
from interfaces import IPositionedView, IEventDisplay

import string

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

def cmp_occurrence(a, b):
    return cmp(a.start, b.start)

class Matrix(object):
    """
    A generic matrix class used to construct our agenda matrix.
    """
    
    def __init__(self, cols=7, rows=5):
        self.cols = cols
        self.rows = rows
        # initialize matrix and fill with ''
        self.matrix = []
        for i in range(rows):
            ea_row = []
            for j in range(cols):
                ea_row.append('')
            self.matrix.append(ea_row)

    def __repr__(self):
        outStr = ""
        for i in range(self.rows):
            #outStr += 'Row %s = %s\n' % (i+1, self.matrix[i])
            outStr += 'Row %s = %s\n' % (i, self.matrix[i])
        return outStr

    def __iter__(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield (self.matrix, row, col)

    def setitem(self, col, row, v):
        self.matrix[col][row] = v
        #self.matrix[col-1][row-1] = v

    def getitem(self, col, row):
        #return self.matrix[col-1][row-1]
        return self.matrix[col][row]

    def getMatrix(self):
        return self.matrix
        
class AgendaView(BaseCalendarView):
    """
    Holds the rendering information for a weekly view which begins
    with today and extends seven days out.
    """

    implements(IUnPositionedView)

    # limit the number of events to be shown
    display_max_events = 5
    
    def calcInfo(self):
        self.calendar = self.context
        # the first day will always be today
        self.today = date.today()
        self.day = self.today.day
        self.month = self.today.month
        self.year = self.today.year
        self.first_day = date(self.year, self.month, self.day)
        self.week = self.first_day.isocalendar()[1]
        
        # self.ends is the day after the last day
        self.ends = self.first_day + timedelta(8)
        self.days = 7 
        # A per viewing cache of which days that have more events than can
        # be displayed, just to avoid searching each day twice.
        self.date_display_maxed = {}
    
    def iterweekdates(self):
        """
        Return an iterator for one week. The iterator yields datetime.date
        values and will iterate through one complete week, beginning with today.
        """
        date = self.today
        # Go back to the beginning of the week
        oneday = timedelta(days=1)
        for i in range(0, 7):
            yield date
            date += oneday
    
    def getShortDate(self, date):
        format = _('%m/%d')
        # %e is the day of month without leading 0 (but with a leading space)
        #format = _('%m/%e')
        return date.strftime(str(format))
    
    def getLongDate(self, date):
        format = _('%B %d, %Y')
        return date.strftime(str(format))

    def getAgendaEvents(self):
        displays = []
        for date in self.iterweekdates():
            occurrences = self.getOccurrencesInDay(date)            
            occurrences.sort(cmp=cmp_occurrence)
            displays.append([getMultiAdapter([occurrence, self], IEventDisplay) for
                        occurrence in occurrences])
        return displays
    
    def getAgendaWeek(self):
        """
        Return a list of items useful for displaying our view.
        """
        DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        
        days = [{'date': date,                                  # datetime
                 'weekday': date.weekday(),                     # e.g. monday is 1
                 'dayname': string.capitalize(DAYS[date.weekday()]),               # e.g. 'Monday'
                 'abbr': 'day-' + DAYS[date.weekday()][:3],     # e.g. 'day-mon'
                 'shortdate': self.getShortDate(date),          # e.g. '4/7/2008'
                 'longdate': self.getLongDate(date),            # e.g. 'April 7, 2008'
                 'extrastyleclass': 'plain'} for date in self.iterweekdates()]
                 
        days[0]['extrastyleclass'] = 'first'
        days[-1]['extrastyleclass'] = 'last'
        
        days[0]['abbr'] = 'day-today'
        days[0]['dayname'] = 'Today'
                
        return days
        
    def getAgendaMatrix(self, days):
        """
        Transpose a list of events by day (the output from getAgendaEvents)
        to a matrix where days are columns and events are rows. This allows us to
        easily build an html table of events, which is constructed row by row.
        
        This is currently not very smart -- empty cells should be concatenated.
        """
        # create matrix with number of days and number of events
        # len(days) should be 7
        a = Matrix(len(days), self.display_max_events)

        # load up the matrix
        for i,r,c in a:
            try:
                i[r][c] = days[c][r]
            except IndexError:
                i[r][c] = '' # we could pass on this
        
        return a.getMatrix()