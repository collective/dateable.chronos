from zope import interface
from zope import schema

class IPossibleCalendar(interface.Interface):
    """A marker interface for representing what *could* be a calendar.
    """

class ICalendarEnhanced(interface.Interface):
    """A marker interface to indicate an item that has calendar functionality.
    """

class IListCalendarEnhanced(ICalendarEnhanced):
    """A marker interface to indicate an item that has calendar functionality
    and should use a list interface instead of a grid interface.
    """

class ICalendarConfig(interface.Interface):
    """Configuration information for a calendar.
    """
    
    calendar_activated = schema.Bool(
        title=u'Calendar Capabilities Activated',
        description=u'Whether calendar capabilities are or should be '
                    u'activated on this item'
        )

class IBasicCalendarSupport(interface.Interface):
    """Provides certain information about calendar support.
    """

    support_enabled = schema.Bool(title=u'Calendar Support Enabled?',
                                  required=True,
                                  readonly=True)

class ICalendarSupport(IBasicCalendarSupport):
    """Provides full information about calendar support.
    """

class IEvent(interface.Interface):
    """An event.
    """
    
    title = schema.TextLine(title=u'Title',
                            required=True,
                            readonly=True)
    description = schema.Text(title=u'Description',
                              required=False,
                              readonly=True)
    start = schema.Datetime(title=u'Start Time',
                            required=True,
                            readonly=True)
    end = schema.Datetime(title=u'End Time',
                          required=False,
                          readonly=True)
    location = schema.TextLine(title=u'Location',
                               required=False,
                               readonly=True)
    local_url = schema.TextLine(title=u'URL',
                                required=True,
                                readonly=True)
    type = schema.TextLine(title=u'Type',
                           required=True,
                           readonly=False)
    timezone = schema.TextLine(title=u'Timezone',
                               required=True,
                               readonly=True)
