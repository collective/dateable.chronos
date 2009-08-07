from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.skin.standardmacros import StandardMacros as BaseMacros

class ChronosMacros(BrowserView):

    template = ViewPageTemplateFile('chronos_macros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]

class StandardMacros(BaseMacros):
    macro_pages = ('minicals',)