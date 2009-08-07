from AccessControl import ClassSecurityInfo
from Products.CMFPlone.CalendarTool import CalendarTool
import interfaces
from datetime import date
import calendar

class ChronosCalendarTool(CalendarTool):
    
    meta_type = "Chronos Calendar Tool"

    def __init__(self):
        self.firstweekday = 0 # 0 is Monday, 6 is Sunday
        self.hour_start = 8
        self.hour_end = 20

    security = ClassSecurityInfo()
    
    security.declarePublic('isCalendar')
    def isCalendar(self, object):
        """is object ICalendarEnchanced provider"""
        return interfaces.ICalendarEnhanced.providedBy(object)

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

    security.declarePrivate('_getCalendar')
    def _getCalendar(self):
        """ Wrapper to ensure we set the first day of the week every time
        """
        calendar.setfirstweekday(self.getFirstWeekDay())
        return calendar
