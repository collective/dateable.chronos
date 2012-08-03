from AccessControl import ClassSecurityInfo
try:
    from Products.Calendaring.tools.calendar import CalendarTool
except ImportError:
    from Products.CMFPlone.CalendarTool import CalendarTool
import calendar
from Products.CMFCore.interfaces import IFolderish

# XXX Stop dependning on portal_calendar. Use a local utility instead.
# (it can depend on portal_calendar, that's ok).

class ChronosCalendarTool(CalendarTool):
    
    meta_type = "Chronos Calendar Tool"

    def __init__(self):
        self.firstweekday = 0 # 0 is Monday, 6 is Sunday
        self.hour_start = 8
        self.hour_end = 20
        self.displaymaxevents = 5
        self.iseventsdisplaylimited = True
        self.dayhourheight = 30 # Two minutes per pixel

    security = ClassSecurityInfo()
    
    security.declarePublic('isCalendar')
    def isCalendar(self, object):
        """Can object be used as a calendar?"""
        return IFolderish.providedBy(object)

    security.declarePublic('getHoursToView')
    def getHoursToView(self):
        """get the hours to display for the day view"""
        return (self.hour_start, self.hour_end)
    
    security.declarePublic('setHoursToView')
    def setHoursToView(self, hour_start, hour_end):
        """set the hours to display for the day view"""
        try:
            hour_start = int(hour_start)
            hour_end = int(hour_end)
            if 0 <= hour_start <= 24:
                self.hour_start = hour_start
            if 0 <= hour_end <= 24:
                self.hour_end = hour_end
        except ValueError:
            pass

    security.declarePublic('getFirstWeekDay')
    def getFirstWeekDay(self):
        """ Get our first weekday setting
        """
        return self.firstweekday

    security.declarePublic('setFirstWeekDay')
    def setFirstWeekDay(self, firstweekday):
        """ Set our first weekday setting
        """
        if firstweekday is not None:
            try:
                fwd = int(firstweekday)
                if 0 <= fwd <= 6:
                    # Do nothing with illegal values
                    self.firstweekday = fwd
            except ValueError:
                # Do nothing with illegal values
                pass
        calendar.setfirstweekday(self.getFirstWeekDay())
        
    security.declarePublic('getMaxEventsToDisplay')
    def getMaxEventsToDisplay(self):
        """ Get max events to display on month view
        """
        return self.displaymaxevents

    security.declarePublic('setMaxEventsToDisplay')
    def setMaxEventsToDisplay(self, maxevents):
        """ Set max events to display on month view
        """
        if maxevents >0:
            self.displaymaxevents = maxevents
            
    security.declarePublic('getIsEventsDisplayLimited')
    def getIsEventsDisplayLimited(self):
        """ Gets if the events display is limited or not
        """
        return self.iseventsdisplaylimited

    security.declarePublic('setIsEventsDisplayLimited')
    def setIsEventsDisplayLimited(self, islimited):
        """ Sets if the events display is limited or not
        """
        self.iseventsdisplaylimited = islimited
        
    security.declarePublic('getDayHourHeight')
    def getDayHourHeight(self):
        """ Gets the hour height
        """
        return self.dayhourheight

    security.declarePublic('setDayHourHeight')
    def setDayHourHeight(self, height):
        """ Sets the hour height
        """
        self.dayhourheight = height

    security.declarePrivate('_getCalendar')
    def _getCalendar(self):
        """ Wrapper to ensure we set the first day of the week every time
        """
        calendar.setfirstweekday(self.getFirstWeekDay())
        return calendar
