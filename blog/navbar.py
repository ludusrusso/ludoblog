from . import nav
from flask_nav.elements import *

from flask_security import current_user
from flask_bootstrap.nav import BootstrapRenderer

from hashlib import sha1
from dominate import tags
from visitor import Visitor


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
        grp = Subgroup(*usergrp)
        grp.right = True
        navbar.items.append(grp)
    else:
        login_view = View('Login', 'security.login')
        login_view.right = True
        navbar.items.append(login_view)
    return navbar

class RightRenderer(BootstrapRenderer):
    def visit_Navbar(self, node):
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')

        if hasattr(node, '_class'):
            root['class'] = node._class
        else:
            root['class'] = 'navbar navbar-default'

        cont = root.add(tags.div(_class='container-fluid'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand',
                                  href=node.title.get_url()))
            elif hasattr(node.title, 'image'):
                header.add(tags.span(tags.img(_src=node.title.image, _class='brand-img'), _class='navbar-brand'))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav'))
        bar_list_right = bar.add(tags.ul(_class='nav navbar-nav navbar-right'))

        for item in node.items:
            if hasattr(item, 'right'):
                bar_list_right.add(self.visit(item))
            else:
                bar_list.add(self.visit(item))
        return root
