import unittest
from Testing.ZopeTestCase import ZopeTestCase
from dateable.chronos.tool import ChronosCalendarTool
from datetime import date

from dateable import kalends        


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
