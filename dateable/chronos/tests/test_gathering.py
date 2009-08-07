from zope.interface.verify import verifyObject
import unittest
from Testing.ZopeTestCase import ZopeTestCase
from dateable.chronos.tool import ChronosCalendarTool
from datetime import date

from dateable import kalends

class EventProviderTestMixin(object):
    """Tests that the EventProvider API is correctly implemented
    Since IEventProvider has no implementation in this product
    these tests must be mixed in with a text that provides an
    event provider as self.provider in the setUp.
    """
    
    def test_interface(self):
        verifyObject(kalends.IEventProvider, self.provider)
        
    def test_gather_all(self):
        all_events = list(self.provider.getOccurrences())
        gathered_events = list(self.provider.getOccurrences())

        self.failUnlessEqual(len(all_events), len(gathered_events))
        
        for i in all_events:
            verifyObject(kalends.IOccurrence, i)
            exists = 0
            for j in gathered_events:
                if (i.title == j.title and 
                    i.start == j.start and
                    i.end   == j.end):
                    exists = True
                    break
            self.failUnless(exists, "Event lists are not equal")
                    
        
    def test_gather_future(self):
        all_events = list(self.provider.getOccurrences())
        if len(all_events) < 2:
            raise ValueError(
                "This test requires you to have at least two events "
                "with non overlapping start and end times.")
        
        # Pick out all the end datetimes for the events:
        end_times = [x.end for x in all_events]
        end_times.sort()
        # Pick an end date in the middle:
        dt = end_times[len(all_events)/2]
        
        # Get all dates starting at or after this middle date
        gathered_events = list(self.provider.getOccurrences(start=dt))
        
        for i in all_events:
            # The event should be returned if the start_date is above
            # or equal the date given as a start date.
            # (It may be expected that events that start before the expected
            # date but continues after it should be included, but this is
            # generally more complicated).
            should_exist = i.start >= dt
            
            # Now check if it exists:
            exists = False
            for j in gathered_events:
                if (i.title == j.title and 
                    i.start == j.start and
                    i.end   == j.end):
                    exists = True
                    break
            self.failUnlessEqual(exists, should_exist, 
                                 "Event lists are not as expected")
        
    def test_title_search(self):
        # This test assumes at least one event, but not all of them
        # has the text "event" in the title.
        all_events = list(self.provider.getOccurrences())
        gathered_events = list(self.provider.getOccurrences(title='event'))

        # Make sure something is returned
        self.failUnless(gathered_events)
        # But not everything
        self.failIfEqual(len(all_events), len(gathered_events))
        
        for i in gathered_events:
            self.failIf(i.title.lower().find('event') == -1)
        


class ChronosToolTest(ZopeTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def afterSetUp(self):
        self.folder._setObject(id='portal_calendar', object=ChronosCalendarTool())
        self.app.REQUEST['SESSION'] = self.Session()

    def test_viewDay(self):
        self.assertEquals(self.folder.portal_calendar.getViewDay(),date.today())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ChronosToolTest)
        ))


if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
