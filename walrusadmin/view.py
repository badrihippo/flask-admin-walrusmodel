from flask.ext.admin.model import BaseModelView
from flask.ext.admin.babel import gettext, ngettext, lazy_gettext
from flask.ext.admin._compat import string_types, iteritems
from flask import flash
import walrus
import wtforms
from .orm import model_form

class ModelView(BaseModelView):

    def __init__(self, model, name=None,
                 category=None, endpoint=None, url=None, static_folder=None,
                 menu_class_name=None, menu_icon_type=None, menu_icon_value=None):
        self._search_fields = []

        super(ModelView, self).__init__(model, name, category, endpoint, url, static_folder,
                                        menu_class_name=menu_class_name,
                                        menu_icon_type=menu_icon_type,
                                        menu_icon_value=menu_icon_value)

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
        columns = dict()
        for n, f in self._get_model_fields():
            # Skip ContainerFields
            if isinstance(f, walrus.models._ContainerField): continue
            columns[n] = f

        return columns

    def init_search(self):
        if self.column_searchable_list:
            for p in self.column_searchable_list:
                if isinstance(p, string_types):
                    p = getattr(self.model, p)

                field_type = type(p)

                # Check type
                if (field_type != walrus.TextField):
                    raise Exception('Can only search on text columns. ' +
                                    'Failed to setup search for "%s"' % p)

                # Check that field is indexed
                if p._index == False:
                    raise Exception('Field must be indexed before searching. ' +
                                    'Please set "index=True" to enable indexing. ' +
                                    'Failed to setup search for "%s"' % p)

                self._search_fields.append(p)

        return bool(self._search_fields)

        if self.column_searchable_list:
            for p in self.column_searchable_list:
                if isinstance(p, string_types):
                    p = getattr(self.model, p)

                field_type = type(p)

                # Check type
                if (field_type != CharField and field_type != TextField):
                        raise Exception('Can only search on text columns. ' +
                                        'Failed to setup search for "%s"' % p)

                self._search_fields.append(p)

        return bool(self._search_fields)

    def scaffold_form(self):
        form_class = model_form(self.model)
        return form_class

    def get_list(self, page, sort_field, sort_desc, search, filters,
        page_size=None):

        # Default query parameters
        expression = None
        order_by = None

        # Search
        if self._search_supported and search:
            # Create a walrus.query.Expression using the first field
            # in the search_fields list
            expression = (self._search_fields[0] == search)

            # Iterate over the remaining search_fields and add
            # them onto the expression (joining them with OR).
            search_fields = self._search_fields[1:]
            for field in search_fields:
                expression = (expression | (field == search))

            # Now we have an expression which says, in effect, "if
            # *at least one* of the fields matches `search`...".

        # Sort
        if sort_field is not None:
            sort_field = self._sortable_columns[sort_field]
            if sort_desc:
                order_by=sort_field.desc()
            else:
                order_by=sort_field

        query = self.model.query(expression=expression, order_by=order_by)
        count = self.model.count()

        return count, query

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
