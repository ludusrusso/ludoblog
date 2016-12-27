from . import nav
from flask_nav.elements import *

@nav.navigation()
def main_nav():
    navbar = Navbar('Blog')
    navbar.items.append(View('Home', 'main.index'))
    return navbar
