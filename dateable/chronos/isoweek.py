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

"""Some handy functions to help dealing with ISO week numbers.
"""

from datetime import datetime, timedelta

def getWeeksInYear(year):
    jan1 = datetime(year, 1, 1)
    dec31 = datetime(year, 12, 31)
    if jan1.isoweekday() == 4 or dec31.isoweekday() == 4:
        return 53
    else:
        return 52

def weeknr2datetime(year, weeknr, weekday=None):
    """
    Return datetime of start of week given year and weeknr.
    
    Optional weekday starts at 1 (monday).
    """
    jan4 = datetime(year, 1, 4)
    iso_year, iso_weeknr, iso_weekday = jan4.isocalendar()
    if iso_weeknr == 1:
        # week1 contains jan4
        week1 = jan4
    else:
        # jan4 is in the last year,
        # so add 7 days to get the next week which should be week 1
        week1 = jan4 + timedelta(7)

    # now adjust week1 so we'll get the start of that week
    week1 = week1 - timedelta(week1.weekday())
    
    # now we have the start date of weeknr 1
    # calculate the start date of the week we want
    result = week1 + timedelta(7 * (weeknr - 1))
    if weekday is not None:
        result = result + timedelta(weekday - 1)
    return result
