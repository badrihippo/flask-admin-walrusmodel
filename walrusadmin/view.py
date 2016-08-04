from flask.ext.admin.model import BaseModelView
from flask.ext.admin.babel import gettext, ngettext, lazy_gettext
from flask.ext.admin._compat import iteritems
from flask import flash
import walrus
import wtforms
from .orm import model_form

class ModelView(BaseModelView):

    def _get_model_fields(self, model=None):
        if model is None:
            model = self.model

        return iteritems(model._fields)
    def get_pk_value(self, model):
        return model.get_id()

    def scaffold_list_columns(self):
        columns = []

        for p, field in self._get_model_fields():
            # Skip ContainerFields
            if isinstance(field, walrus.models._ContainerField): continue

            # Add field to list
            columns.append(p)

        return columns

    def scaffold_sortable_columns(self):
        return None

    def init_search(self):
        return None

    def scaffold_form(self):
        form_class = model_form(self.model)
        return form_class

    def get_list(self, page, sort_field, sort_desc, search, filters,
        page_size=None):
        model_list = self.model.all()
        model_count = self.model.count()
        return model_count, model_list

    def get_one(self, id):
        return self.model.load(id)

    def create_model(self, form):
        try:
            model = self.model()
            form.populate_obj(model)
            model.save()
        except Exception as e:
            if not self.handle_view_exception(e):
                flash(gettext('Failed to create record. %(error)s', error=str(e)), 'error')
            return False

        return model

    def update_model(self, form, model):
        try:
            form.populate_obj(model)
            model.save()
        except Exception as e:
            if not self.handle_view_exception(e):
                flash(gettext('Failed to update record. %(error)s', error=str(e)), 'error')
            return False

        return True

    def delete_model(self, model):
        try:
            model.delete()
        except Exception as e:
            flash(gettext('Failed to update record. %(error)s', error=str(e)), 'error')
            return False

        return True
