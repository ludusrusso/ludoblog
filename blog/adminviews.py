from flask_superadmin import expose, AdminIndexView as _AdminIndexView
from flask_superadmin.model import ModelAdmin as _ModelAdmin
from flask_security import current_user
from flask import abort

class ModelAdmin(_ModelAdmin):
    def is_accessible(self):
        return current_user.has_role('admin')

    def _handle_view(self, name, *args, **kwargs):
        if not self.is_accessible():
            abort(403)


class AdminIndexView(_AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.has_role('admin'):
            abort(403)
        return super(AdminIndexView, self).index()
