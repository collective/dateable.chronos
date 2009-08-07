from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ChronosPopup(BrowserView):

    index = ViewPageTemplateFile('chronos_popup.pt')
     
#    def __call__(self):
#       return self.template

    def __getitem__(self, key):
        return self.index.macros[key]
