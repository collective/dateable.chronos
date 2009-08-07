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
from zope.schema import Int, Date, Datetime, TextLine, Text, Bool, Choice, Set
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
    
    width = Int(title=_(u"Width"), 
                description=_(u"The total width of the view"))
    
    height = Int(title=_(u"Height"), 
                description=_(u"The total height of the view"))
    
    first_day = Date(title=_(u"First Day"),
                     description=_(u"The first day of the view"))
    
    days = Int(title=_(u"Days"), 
               description=_(u"The number of days shown"))

    from_hour = Int(title=_(u"From hour"), 
                    description=_(u"The time at the top of the view"))

    to_hour = Int(title=_(u"To hour"), 
                  description=_(u"The time at the bottom of the view"))


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

class IEventEditSchema(Interface):
    title = TextLine(
        title=_(u"Title"),
        description=_(u"The title of the event."))

    description = Text(
        title=_(u"Description"),
        required=False,
        description=_(u"A description of the event."))

    dtstart = Datetime(title=_(u"Starts"),
                       description=_(u"Date and time when this event starts."))

    dtend = Datetime(title=_(u"Ends"),
                     description=_(u"Date and time when this event ends."))

    allday = Bool(
        title=_(u"Takes all day"),
        description=_(u"Check this box if the event goes on all day"),
        required=False)

    transparent = Bool(
        title=_(u"Not busy"),
        description=_(u"This event should not appear as busy time in the meeting helper."),
        required=False)
          
    location = Text(
        title=_(u"Location"),
        required=False,
        description=_(u"The location where this event takes place."))
    
    status = Choice(
        title=_(u"Status"),
        vocabulary='CalendarEventStatus',
        description=_(u"The status of the event."),
        required=True,
        default='CONFIRMED')

    access = Choice(
        title=_(u"Access"),
        vocabulary='CalendarEventAccess',
        description=_(u"Who has access to this event."),
        required=True,
        default='PUBLIC')

    document = TextLine(
        title=_(u"Document"),
        required=False,
        description=_(u"A document related to this event."))
    
    categories = Set(
        title=_(u"Categories"),
        description=_(u"Categories for this event"),
        value_type=Text(),
        required=False)
    
class INavigation(IViewletManager):
    """A viewlet manager for navigation dropdowns
    """
