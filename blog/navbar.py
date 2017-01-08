from . import nav
from flask_nav.elements import *

from flask_security import current_user

@nav.navigation()
def main_nav():
    navbar = Navbar('Blog')
    navbar.items.append(View('Home', 'main.index'))
    if current_user.is_authenticated:
        usergrp = []
        usergrp.append(current_user.email)
        if current_user.has_role('admin'):
            usergrp.append(View('Admin', 'admin.index'))
        usergrp.append(View('Logout', 'security.logout'))
        navbar.items.append(Subgroup(*usergrp))
    return navbar
