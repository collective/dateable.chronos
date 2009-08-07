## Controller Python Script "Save Chronos configuration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Save Chronos configuration
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST

first_week_day = context.REQUEST.get('first_week_day', None)
hour_start = context.REQUEST.get('hour_start', None)
hour_end = context.REQUEST.get('hour_end', None)
islimited = context.REQUEST.get('is-limited', None)
maxevents = context.REQUEST.get('max-events', None)
dayhourheight = context.REQUEST.get('day-hour-height', None)

if first_week_day:
    first_week_day = 6
else:
    first_week_day = 0
calendar_tool = getToolByName(context, 'portal_calendar')
calendar_tool.setFirstWeekDay(first_week_day)
calendar_tool.setHoursToView(hour_start, hour_end)
if islimited == '1':
    calendar_tool.setIsEventsDisplayLimited(True)
else:
    calendar_tool.setIsEventsDisplayLimited(False)
calendar_tool.setMaxEventsToDisplay(int(maxevents))
calendar_tool.setDayHourHeight(int(dayhourheight))

from Products.CMFPlone.utils import transaction_note
transaction_note('Reconfigured chronos')

context.plone_utils.addPortalMessage(_(u'Chronos reconfigured.'))
return state
