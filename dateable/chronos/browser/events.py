import datetime
from dateable import kalends
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
        now = datetime.datetime.now()
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
        now = datetime.datetime.now()
        months = self._getEventList(start=now)
        return self.eventlist(months=months, show_past=False)

    def pastEvents(self):
        now = datetime.datetime.now()
        months = self._getEventList(stop=now)
        return self.eventlist(months=months, show_past=True)

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
