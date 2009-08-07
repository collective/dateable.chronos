from DateTime import DateTime
from Testing.ZopeTestCase.utils import setupCoreSessions

from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer

from dateable.chronos.interfaces import ICalendarConfig

PloneTestCase.setupPloneSite()

class TestTest(PloneTestCase.FunctionalTestCase):
    def eventSetUp(self):
        self.loginAsPortalOwner()
        # Create folder.
        self.portal.invokeFactory('Folder', id='calendar-folder')
        cal = self.portal['calendar-folder']
        id = cal.invokeFactory('Event', id='event1')
        cal['event1'].update(title='First Event',
                             startDate=DateTime('2006-09-28 08:30am GMT+0'),
                             endDate=DateTime('2006-09-28 09:30am GMT+0'))
        id = cal.invokeFactory('Event', id='event2')
        cal['event2'].update(title='Second Event',
                             startDate=DateTime('2006-09-29 08:30am GMT+0'),
                             endDate=DateTime('2006-09-29 09:30am GMT+0'))
        id = cal.invokeFactory('Event', id='meeting1')
        # Calling this event "Meeting" is just to have one event that does
        # not have the word "Event" in the title.
        cal['meeting1'].update(title='First Meeting',
                               startDate=DateTime('2006-09-30 08:30am GMT+0'),
                               endDate=DateTime('2006-09-30 09:30am GMT+0'))

        # Lets pop in an event that happens right now, and should end up
        # in all the default views:
        id = cal.invokeFactory('Event', id='now')
        cal['now'].update(title='Now',
                               startDate=DateTime(),
                               endDate=DateTime() + 1.0/24.0)

        # Activate calendaring capabilities on this folder
        config = ICalendarConfig(cal)
        config.calendar_activated = True
        self.login(PloneTestCase.default_user)
            
    def afterSetUp(self):
        setupCoreSessions(self.app)
        self.addProduct('chronos')
        self.site_url =  self.portal.absolute_url()
        self.eventSetUp()

    def test_basic(self):
        browser = Browser()
        browser.open(self.site_url+'/calendar-folder')
        # For each of the views, the "Now" event should show up:
        browser.getLink('Now')
        browser.getLink('Week').click()
        browser.getLink('Now')
        browser.getLink('Day').click()
        browser.getLink('Now')
        browser.getLink('List').click()
        browser.getLink('Now')
        browser.getLink('Past').click()
        browser.getLink('Now')
    

def test_suite():
    from unittest import TestSuite, makeSuite
    
    suite = TestSuite()
    suite.addTests(makeSuite(TestTest))
    suite.layer = layer.ZCMLLayer

    return suite
