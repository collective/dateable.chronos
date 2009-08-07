class ChronosStyle(object):
    """ view class to allow us to use portal props in our CSS """

    def getBaseProps(self):
        return self.context.base_properties
