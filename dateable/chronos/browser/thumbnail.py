from time import localtime

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.viewlet.interfaces import IViewlet, IViewletManager

from kss.core import KSSView, kssaction

from Acquisition import aq_inner

from Products.PythonScripts.standard import url_quote_plus
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

PLMF = MessageFactory('plonelocales')

class NavigationView(KSSView):

    @kssaction
    def navigationChange(self, month, year, viewname):
        core = self.getCommandSet('core')
        manager = getMultiAdapter((core.context, core.request, core.view,),
                                  IViewletManager, name='chronos.navigation')
        renderer = getMultiAdapter(
            (core.context, core.request, core.view, manager),
            IViewlet,
            name='chronos.ajaxnavigation'
        )
        renderer = renderer.__of__(self.context)
        renderer.update(int(month), int(year), viewname)

        result = renderer.render()
        core.replaceInnerHTML('#chronosPopupCalendar', result)


# This is a mildly modified copy of the standard plone calendar portlet:
class ThumbnailMonth(BrowserView):

    implements(IViewlet)

    render = ViewPageTemplateFile('thumbnail.pt')

    updated = False

    def __init__(self, context, request, view, manager):
        super(ThumbnailMonth, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self, month=None, year=None, viewname=None):
        if self.updated:
            return
        self.updated = True

        if viewname is None:
            viewname = self.view.__name__
        self.viewname = viewname

        context = aq_inner(self.context)
        self.calendar = getToolByName(context, 'portal_calendar')
        self._ts = getToolByName(context, 'translation_service')
        self.url_quote_plus = url_quote_plus

        self.now = localtime()
        if month is None or year is None:
            self.yearmonth = yearmonth = self.getYearAndMonthToDisplay()
            self.year = year = yearmonth[0]
            self.month = month = yearmonth[1]
        else:
            self.yearmonth = yearmonth = (year, month)
            self.year = year
            self.month = month

        self.showPrevMonth = yearmonth > (self.now[0]-1, self.now[1])
        self.showNextMonth = yearmonth < (self.now[0]+1, self.now[1])

        self.prevMonthYear, self.prevMonthMonth = self.getPreviousMonth(year, month)
        self.nextMonthYear, self.nextMonthMonth = self.getNextMonth(year, month)

        self.monthName = PLMF(self._ts.month_msgid(month),
                              default=self._ts.month_english(month))


    def getEventsForCalendar(self):
        year = self.year
        month = self.month
        weeks = self.calendar.getEventsForCalendar(month, year)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                day['date_string'] = '%s-%s-%s' % (year, month, daynumber)
        return weeks

    def getEventString(self, event):
        start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
        end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
        title = safe_unicode(event['title']) or u'event'

        if start and end:
            eventstring = "%s-%s %s" % (start, end, title)
        elif start: # can assume not event['end']
            eventstring = "%s - %s" % (start, title)
        elif event['end']: # can assume not event['start']
            eventstring = "%s - %s" % (title, end)
        else: # can assume not event['start'] and not event['end']
            eventstring = title

        return eventstring

    def getYearAndMonthToDisplay(self):
        session = None
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if self.calendar.getUseSession():
            session = request.get('SESSION', None)
            if session:
                if not year:
                    year = session.get('calendar_year', None)
                if not month:
                    month = session.get('calendar_month', None)

        # Last resort to today
        if not year:
            year = self.now[0]
        if not month:
            month = self.now[1]

        year, month = int(year), int(month)

        # Store the results in the session for next time
        if session:
            session.set('calendar_year', year)
            session.set('calendar_month', month)

        # Finally return the results
        return year, month

    def getPreviousMonth(self, year, month):
        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1
        return (year, month)

    def getNextMonth(self, year, month):
        if month==12:
            month, year = 1, year + 1
        else:
            month+=1
        return (year, month)

    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""
        weekdays = []
        # list of ordered weekdays as numbers
        for day in self.calendar.getDayNumbers():
            weekdays.append(PLMF(self._ts.day_msgid(day, format='s'),
                                 default=self._ts.weekday_english(day, format='a')))

        return weekdays

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """
        return self.now[2]==day and self.now[1]==self.month and \
               self.now[0]==self.year

    def getReviewStateString(self):
        states = self.calendar.getCalendarStates()
        return ''.join(map(lambda x : 'review_state=%s&amp;' % self.url_quote_plus(x), states))

    def getQueryString(self):
        request = self.request
        query_string = request.get('orig_query',
                                   request.get('QUERY_STRING', None))
        if len(query_string) == 0:
            query_string = ''
        else:
            query_string = '%s&amp;' % query_string
        return query_string

