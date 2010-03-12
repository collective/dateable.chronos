from unittest import TestCase, makeSuite, TestSuite
from dateable.chronos.utils import localTimeFormatFromLocalDateTimeFormat

class TestSequenceFunctions(TestCase):
    def test_inference(self):
        """Make sure our crazy localTimeOnlyFormat function works."""
        # Test every combination: datelike-to-nondatelike, nondatelike-to-datelike, datelike-to-datelike, and nondatelike-to-nondatelike:
        self.assertEqual(localTimeFormatFromLocalDateTimeFormat("ab: %H:%I at %a-%Y"), '%H:%I')

        # Test beginning with a token, ending with an unknown token, and having tokens run right up against each other:
        self.assertEqual(localTimeFormatFromLocalDateTimeFormat("%Sab: %H:%I%I at %a-%Y %?"), '%Sab: %H:%I%I%?')

        # Test some other cases I no longer remember:
        self.assertEqual(localTimeFormatFromLocalDateTimeFormat("%b %d, %Y %I:%M %p"), '%I:%M %p')

        # Test adjacent % signs:
        self.assertEqual(localTimeFormatFromLocalDateTimeFormat("b %%% smoo"), '% ')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSequenceFunctions))
    return suite

