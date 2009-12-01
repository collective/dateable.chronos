import Products.CMFCore.utils
from dateable.chronos import tool

from config import SKINS_DIR, GLOBALS

from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory(SKINS_DIR, GLOBALS)

from zope.i18nmessageid import MessageFactory
chronosMessageFactory = MessageFactory('chronos')
from Products.PlacelessTranslationService.utility import PTSTranslationDomain
chronosdomain = PTSTranslationDomain('chronos')

def initialize(context):

    Products.CMFCore.utils.ToolInit('Chronos Calendar Tool', 
                                    tools=(tool.ChronosCalendarTool,), 
                                    product_name='chronos', 
                                    icon='tool.gif',  
                                    ).initialize(context) 