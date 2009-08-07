from zope.formlib import form
from dateable.chronos import interfaces

class ConfigView(form.PageEditForm):
    """Calendar configuration.
    """
    
    form_fields = form.FormFields(interfaces.ICalendarConfig)
