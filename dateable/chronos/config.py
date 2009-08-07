PROJECTNAME = 'chronos'
SKINS_DIR = 'skins'

GLOBALS = globals()

install_soft_dependecies = 0

# List of hard dependencies that will be installed when chronos is installed
DEPENDENT_PRODUCTS = [
    ]

SOFT_DEPENDENT_PRODUCTS = [
    ]

if install_soft_dependecies:
    DEPENDENT_PRODUCTS = DEPENDENT_PRODUCTS + SOFT_DEPENDENT_PRODUCTS