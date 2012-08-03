# Obsolete
import sys
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.interfaces import IFolderish

if sys.version_info < (2, 6):
    # Plone 3
    from Products.CMFDynamicViewFTI.interfaces import IDynamicallyViewable
else:
    # Plone 4
    from Products.CMFDynamicViewFTI.interfaces import IDynamicViewTypeInformation as IDynamicallyViewable


class CalendarDynamicViews(object):
    
    implements(IDynamicallyViewable)
    adapts(IFolderish)
    

    def __init__(self, context):
        self.context = context # Actually ignored...
        
    def getAvailableViewMethods(self):
        """Get a list of registered view method names
        """
        return [x[0] for x in self.getAvailableLayouts()]

    def getDefaultViewMethod(self):
        """Get the default view method name
        """
        return "month.html"

    def getAvailableLayouts(self):
        """Get the layouts registered for this object.
        """        
        return (("day.html", "Day list"),
                ("week.html", "Week list"),
                ("month.html", "Month view"),
                ("list.html", "Event list"),
                ("past.html", "Event archive"),
                )
