import sys
import BTrees
import datetime
import calendar
from Acquisition import aq_inner
from ZTUtils import make_query

from AccessControl import getSecurityManager
from zope.interface import implements
from zope.component import queryMultiAdapter, getAdapters, getUtility, getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.app.publisher.interfaces.browser import IBrowserMenu

from Products.CMFCore.utils import getToolByName
from dateable.chronos import utils
from dateable.chronos.browser.interfaces import ICalendarView

from dateable import kalends

from Products.Five.browser import BrowserView

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

# This evilness must go:
DAYS = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
        ]

# And this too
MONTHS = [
          'N/A',
          'January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December',
          ]

ONEDAY = datetime.timedelta(days=1)

CALENDAR_VIEWS = (("day.html", "Day list"),
                  ("week.html", "Week list"),
                  ("month.html", "Month view"),
                  ("list.html", "Event list"),
                  ("past.html", "Event archive"),
                  )

def derive_ampmtime(timeobj):
    """Derives the 12 hour clock am/pm identifier and proper hour.

    Some random tests.

      >>> from datetime import time

      >>> derive_ampmtime(time(1, 30))
      (1, 'a')

      >>> derive_ampmtime(time(13, 30))
      (1, 'p')

      >>> derive_ampmtime(time(12, 01))
      (12, 'p')

      >>> derive_ampmtime(time(23, 59))
      (11, 'p')

    """
    
    hour = timeobj.hour
    ampm = 'a'
    if hour == 12:
        ampm = 'p'
    elif hour > 12:
        hour -= 12
        ampm = 'p'

    return (hour, ampm)

def tiny_time(dt):
    """Return a clean label representing the given event.
    
    Necessary imports.
    
      >>> from datetime import datetime
      
    Make sure the label is clean.
    
      >>> tiny_time(datetime(2006, 9, 30, 9, 30))
      '9:30'
      
      >>> tiny_time(datetime(2006, 9, 30, 9, 0))
      '9'

      >>> tiny_time(datetime(2006, 9, 30, 13, 0))
      '1p'

      >>> tiny_time(datetime(2006, 9, 30, 13, 20))
      '1:20p'
    """
    
    hour, ampm = derive_ampmtime(dt)
    if ampm == 'a':
        ampm = ''
    minutes = ''
    if dt.minute != 0:
        minutes = ':%02i' % dt.minute
    
    time = str(hour) + minutes + ampm
    
    return time

def monthweeks(year=None, month=None, daydate=None, firstweekday=None):
    """Return an iterable of week tuples where each element in the week
    tuple is an instance of *datetime.date*.  If *daydate* is ommitted
    then the date chosen is based on the *year* and *month*.
    
    The following are equivalent.
    
      >>> from datetime import date
      >>> import calendar
      
    Using a daydate means the actual day gets ignored.

      >>> list(monthweeks(2006, 2)) == \\
      ...     list(monthweeks(daydate=date(2006, 2, 13)))
      True
      
    Now lets check out some week day values.
    
      >>> weeks = list(monthweeks(2006, 2, firstweekday=calendar.SUNDAY))
      >>> weeks[0][0]
      datetime.date(2006, 1, 29)
      
    The last day of the first week will be February 4, 2006.

      >>> weeks[0][-1]
      datetime.date(2006, 2, 4)
      
    The first day of the last week will be February 26, 2006.

      >>> weeks[-1][0]
      datetime.date(2006, 2, 26)

    The last day of the last week will be March 4, 2006.
    
      >>> weeks[-1][-1]
      datetime.date(2006, 3, 4)

    For a month where the last day of the month is the last day of the
    week.
    
      >>> weeks = list(monthweeks(2006, 9, firstweekday=calendar.SUNDAY))
      >>> weeks[-1][-1]
      datetime.date(2006, 9, 30)

    At one point when you used the last month while retrieving the weeks
    it would send the mechanism into an infinite loop until it raised 
    OverflowError.  Lets make sure that doesn't happen again.

      >>> weeks = list(monthweeks(daydate=date(2006, 12, 1), 
      ...                         firstweekday=calendar.SUNDAY))
      >>> weeks[0][0]
      datetime.date(2006, 11, 26)
      >>> weeks[-1][-1]
      datetime.date(2007, 1, 6)
      
    And now for testing another year.
    
      >>> weeks = list(monthweeks(2007, 1, firstweekday=calendar.SUNDAY))
      >>> weeks[0][0]
      datetime.date(2006, 12, 31)

    One last test, lets cycle through the months over a multi-year period
    and make sure we don't get any OverflowError's.
    
      >>> count = 0
      >>> for year in range(2002, 2006):
      ...     for month in range(1, 13):
      ...         x = monthweeks(year, month, firstweekday=calendar.SUNDAY)
      ...         x = monthweeks(year, month, firstweekday=calendar.MONDAY)
      ...         count += 1
      >>> count
      48

    """
    
    if firstweekday == None:
        firstweekday = calendar.firstweekday()

    if firstweekday == 0:
        lastweekday = 6
    else:
        lastweekday = firstweekday - 1
    
    if daydate is None:
        today = datetime.date.today()
        y = year or today.year
        m = month or today.month
        firstdate = datetime.date(y, m, 1)
    else:
        firstdate = datetime.date(daydate.year,
                                  daydate.month,
                                  1)

    firstcalday = firstdate
    while calendar.weekday(firstcalday.year, 
                           firstcalday.month, 
                           firstcalday.day) != firstweekday:
        firstcalday -= ONEDAY
    
    weeks = []
    day = firstcalday
    nextday = day + ONEDAY
    weekday = calendar.weekday(day.year, day.month, day.day)

    # see if block at bottom of while block for break conditions
    max = 100
    count = 0
    while count < max:
        if weekday == firstweekday:
            week = []
            weeks.append(week)
        week.append(day)
        
        if weekday == lastweekday:
            if nextday.month > firstdate.month or \
                  nextday.year > firstdate.year:
                break

        day += ONEDAY
        nextday = day + ONEDAY
        weekday = calendar.weekday(day.year, day.month, day.day)

        count += 1

    if count == max:
        raise OverflowError('Counted %i days for this interval which is '
                            'not possible, something went wrong' % max)

    return (tuple(x) for x in weeks)


class ViewableDay(object):

    def __init__(self, daydate):
        self._eventset = None
        self.extrastyleclass = ''
        self.daydate = daydate

    def add(self, obj):
        # lazily set the eventset as a BTree
        if self._eventset is None:
            self._eventset = BTrees.OOBTree.OOTreeSet()
        self._eventset.insert(obj)

    @property
    def allevents(self):
        if self._eventset is None:
            return []
        all = list(self._eventset)
        return all

    @property
    def events(self):
        return self.allevents[:2]

    @property
    def datestr(self):
        return '%04i-%02i-%02i' % (self.daydate.year,
                                   self.daydate.month,
                                   self.daydate.day)

    @property
    def day(self):
        return self.daydate.day

    @property
    def has_more(self):
        return len(self._eventset) > 2


class BaseCalendarView(BrowserView):
    """Base view for the calendar views.
    """
    
    implements(ICalendarView)

    def __init__(self, context=None, request=None):
        if context is not None:
            self.context = context
        if request is not None:
            self.request = request
        
        self._cached_weeks = {}
        self._cached_alldays = {}
        self.calendar_tool = getToolByName(self.context, 'portal_calendar')

    def _set_default_day(self, defaultday):
        self._default_day = defaultday
        utils.set_view_day(self.request, defaultday)

    def _get_default_day(self):
        if hasattr(self, '_default_day'):
            return self._default_day
        
        if not hasattr(self, 'request'):
            self._default_day = utils.get_view_day(self.request)

            return self._default_day
        
        year = self.request.form.get('year', None)
        month = self.request.form.get('month', None)
        
        if month is None:
            return utils.get_view_day(self.request)

        t = utils.get_view_day(self.request)
        year = year or t.year
        year = int(year)
        month = int(month)
        
        self._default_day = datetime.datetime(year, month, 1)
        self._set_default_day(self._default_day)
        
        return self._default_day
    
    default_day = property(_get_default_day, _set_default_day)

    def __set_firstweekday(self, firstweekday):
        self._firstweekday = firstweekday
    def __get_firstweekday(self):
        first = getattr(self, '_firstweekday', None)
        if first is not None:
            return first
        first = int(self.request.form.get('firstweekday', 
                                          calendar.firstweekday()))
        self._firstweekday = first
        return first
    
    firstweekday = property(__get_firstweekday, __set_firstweekday)
    
    def view_tabs(self):
        """ Returns the list of views to build the view tabs with """
        menu = getUtility(IBrowserMenu, 'chronos_views')
        actions = {}
        for name, item in getAdapters((self.context, self.request),
                                      menu.getMenuItemType()):
            if item.available():
                actions[item.action] = item
        # Sort results from the default view:
        result = []
        for action, title in CALENDAR_VIEWS:
            if action in actions.keys():
                result.append(actions[action])
                del actions[action]
        result.extend(actions.values())
        return result

    def check_permission(self, permission, object=None):
        if object is None:
            object = self.context
        user = getSecurityManager().getUser()
        return user.has_permission(permission, object)
    
    def get_short_date(self, date):
        format = _('%d/%m')
        return date.strftime(str(format))

    def standard_week_days(self, firstweekday=None):
        """Return the standard days of the week starting with the day
        that is most appropriate as the start day for the current locale.
        
        As an example, make sure using 6 as the first work day chooses a 
        week starting with Sunday.
        
          >>> mt = MonthView()
          >>> days = mt.standard_week_days(6)
          >>> days[0]
          {'extrastyleclass': 'first-week-day', 'day': 'Sunday'}
          >>> days[-1]
          {'extrastyleclass': 'last-week-day', 'day': 'Saturday'}
        """
        
        if firstweekday is None:
            firstweekday = self.firstweekday
        
        days = [{'day': x,
                 'extrastyleclass': ''} for x in DAYS[firstweekday:]]
        days += [{'day': x,
                  'extrastyleclass': ''} for x in DAYS[0:firstweekday]]

        days[0]['extrastyleclass'] = 'first-week-day'
        days[-1]['extrastyleclass'] = 'last-week-day'
        
        return days

    def getOccurrencesInDay(self, day):
        start = datetime.datetime.combine(day, datetime.time(0,0))
        end = datetime.datetime.combine(day, datetime.time(23,59,59))
        return self.getOccurrences(start, end)

    def getOccurrences(self, start, end):
        provider = kalends.IEventProvider(self.context)
        return provider.getOccurrences(start, end, **self.request.form)

    def month(self):
        return MONTHS[self.default_day.month]
    
    def year(self):
        return '%04i' % self.default_day.year

    def week(self):
        """ Return the week number """
        return self.default_day.isocalendar()[1]

    def next_day_link(self):
        next_day = self.default_day + datetime.timedelta(days=1)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               next_day.year,
                                               next_day.month,
                                               next_day.day)

    def prev_day_link(self):
        previous_day = self.default_day + datetime.timedelta(days=-1)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               previous_day.year,
                                               previous_day.month,
                                               previous_day.day)

    def next_week_link(self):
        next_week = self.default_day + datetime.timedelta(days=7)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               next_week.year,
                                               next_week.month,
                                               next_week.day)

    def prev_week_link(self):
        previous_week = self.default_day + datetime.timedelta(days=-7)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               previous_week.year,
                                               previous_week.month,
                                               previous_week.day)

    def next_month_link(self):
        if self.default_day.month == 12:
            next_month = self.default_day.replace(month=1, year=self.default_day.year+1)
        else:
            next_month = self.default_day.replace(month=self.default_day.month+1)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               next_month.year,
                                               next_month.month,
                                               next_month.day)

    def prev_month_link(self):
        if self.default_day.month == 1:
            previous_month = self.default_day.replace(month=12, year=self.default_day.year-1)
        else:
            previous_month = self.default_day.replace(month=self.default_day.month-1)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               previous_month.year,
                                               previous_month.month,
                                               previous_month.day)

    def next_year_link(self):
        next_year = self.default_day.replace(year=self.default_day.year+1)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               next_year.year,
                                               next_year.month,
                                               next_year.day)

    def prev_year_link(self):
        previous_year = self.default_day.replace(year=self.default_day.year+1)
        return '%s?year=%s&month=%s&day=%s' % (self.context.absolute_url(),
                                               previous_year.year,
                                               previous_year.month,
                                               previous_year.day)

    def render_filter(self):
        provider = queryMultiAdapter(
            (self.context, self.request, self), 
            IContentProvider, 'eventfilter')
        if provider is None:
            return ''
        provider.update()
        return provider.render()

    def url(self, start=None, stop=None):
        provider = kalends.IWebEventCreator(self.context.context)
        return provider.url(start, stop)

    def getDateUrl(self, day, type):
        return '%s/%s.html?date=%s' % (self.context.absolute_url(),
                                       type,
                                       day.strftime('%Y-%m-%d'))

    def canCreateEvents(self):
        for id, creator in getAdapters((self.context,), kalends.IWebEventCreator):
            if creator.canCreate():
                return True
        return False
    
    def getEventCreationLink(self, day=None, time=None):
        # XXX We need to support multiple links.
        for id, creator in getAdapters((self.context,), kalends.IWebEventCreator):
            if not creator.canCreate():
                continue
            if day is None and time is None:
                start = end = None
            else:
                if time is None:
                    time = datetime.time()
                start = datetime.datetime.combine(day, time)
                end = start + datetime.timedelta(seconds=3600)
            return creator.url(start, end)
        # Actually, raising an error would be better:
        return ''
    
    def _getTimeFormatter(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state.locale().dates.getFormatter('time', 'short')

    def localizedHour(self, hour):
        # Get the date format from the locale
        return self._getTimeFormatter().format(datetime.time(hour, 0))

    def get_action_url(self, action):
        form = self.request.form.copy()
        if '-C' in form:
            del form['-C']
        query = make_query(form)
        if query:
            return "%s?%s" % (action, query)
        return action
        
    def popup_in_tabs(self):
        return False

