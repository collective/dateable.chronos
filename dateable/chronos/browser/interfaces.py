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
# $Id: interfaces.py 50554 2006-12-12 15:41:10Z lregebro $
"""
  interfaces.py
"""
from zope.interface import Interface
from zope.schema import Int, Date
from zope.viewlet.interfaces import IViewletManager

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

class ICalendarView(Interface):
    """Any view on the calendar"""
    pass

class IUnPositionedView(ICalendarView):
    """A view that uses no positioning to render events (month view)"""
    pass

class IPositionedView(ICalendarView):
    """A view that uses absolute positioning to render events"""

    width = Int(title=u"Width",
                description=u"The total width of the view")

    height = Int(title=u"Height",
                description=u"The total height of the view")

    first_day = Date(title=u"First Day",
                     description=u"The first day of the view")

    days = Int(title=u"Days",
               description=u"The number of days shown")

    from_hour = Int(title=u"From hour",
                    description=u"The time at the top of the view")

    to_hour = Int(title=u"To hour",
                  description=u"The time at the bottom of the view")


class IEventPosition(Interface):
    """An events position

    Contains the information needed to properly display an event on a
    IPositionedView."""

    def getCssPositionString():
        """Returns a properly formatted css-style position string.

        Usage in the template:
          tal:attributes=_(u"style event_render_info/getCssPositionString"
        """

class IEventDisplay(Interface):
    """An events display information

    Contains the information needed to properly display an event on a
    IPositionedView."""

    def getCssPositionString():
        """Returns a properly formatted css-style position string.

        Usage in the template:
          tal:attributes=_(u"style event_render_info/getCssPositionString"
        """

    def getCssStatusClass(self):
        """Returns a CSS class name according to the status of this event
        for the current user attendee (if there is one). Possible classes are:

            need-action
            accepted
            declined
            tentative
            delegated
            <empty>

        It is up to the actual stylesheet to do something with this class.
        """

class INavigation(IViewletManager):
    """A viewlet manager for navigation dropdowns
    """
