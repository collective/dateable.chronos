import datetime
from dateable import kalends
from dateable.chronos import isoweek
try:
    from Products.Five.browser.pagetemplatefile import \
         ZopeTwoPageTemplateFile as PageTemplateFile
except ImportError:
    from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from base_view import BaseCalendarView

class EventListingView(BaseCalendarView):
    """View that lists events.
    """

    eventlist = PageTemplateFile('events.pt')

    def _getEventList(self, start=None, stop=None):
        provider = kalends.IEventProvider(self.context)
        events = list(provider.getOccurrences(start=start, stop=stop,
                                             **self.request.form))
        events.sort()
        months = []
        month_info = []
        old_month_year = None
        for event in events:
            start = event.start
            month = str(start.month)
            year = str(start.year)
            month_year = year+month
            if month_year != old_month_year:
                old_month_year = month_year
                if month_info:
                    months.append(month_info)
                month_info = {'month': start.month,
                              'year': start.year,
                              'month_name': start.strftime("%B"),
                              'events': []}
            event_dict = {'event': event,
                          'day': start.day,
                          'title': event.title,
                          'description': event.description,
                          'location': event.location,
                          'url': event.url,
                          }
            month_info['events'].append(event_dict)

        if month_info:
            months.append(month_info)

        return months

    def upcomingEvents(self):
        """Show all upcoming events"""
        now = datetime.datetime.now()
        months = self._getEventList(start=now)
        return self.eventlist(months=months, show_past=False)

    def pastEvents(self):
        """Show all past events"""
        now = datetime.datetime.now()
        months = self._getEventList(stop=now)
        return self.eventlist(months=months, show_past=True)

    def monthEvents(self):
        """Show all events for a particular month"""
        month = self.default_day.month
        year = self.default_day.year
        # Start of this month
        start = datetime.datetime(year, month, 1)
        # calculate the start date of the next month
        if month == 12:
            stop = datetime.datetime(year+1, 1, 1)
        else:
            stop = datetime.datetime(year, month+1, 1)
        months = self._getEventList(start=start,stop=stop)
        return self.eventlist(months=months, show_past=True)

    def weekEvents(self):
        """Show all events for a particular week"""
        start = isoweek.weeknr2datetime(self.default_day.year, self.week(), 1)
        stop = start + datetime.timedelta(7)
        months = self._getEventList(start=start,stop=stop)
        return self.eventlist(months=months, show_past=True)

    def dayEvents(self):
        """Show all events for a particular day"""
        start = datetime.datetime.combine(self.default_day, datetime.time(0,0))
        months = self._getEventList(start=start,
                                    stop=start + datetime.timedelta(1))
        return self.eventlist(months=months, show_past=True)

    def popup_in_tabs(self):
        # The popup needs to be in the tabs for the list views,
        # but it makes no sense for the list and past view:
        return self.__name__ not in (u'list.html', u'past.html')

    def url(self, start=None, stop=None):
        provider = kalends.IWebEventCreator(self.context)
        return provider.url(start, stop)

    def render_filter(self):
        provider = queryMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, 'eventfilter')
        if provider is None:
            return ''
        provider.update()
        return provider.render()
