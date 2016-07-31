from flask.ext.admin.model import BaseModelView
import walrus
import wtforms
from .orm import model_form

class ModelView(BaseModelView):
    def get_pk_value(self, model):
        return model.get_id()

    def scaffold_list_columns(self):
        columns = []

        for p in self.model._fields.keys():
            field = getattr(self.model, p)

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
        print model_count, model_list
        return model_count, model_list

    def get_one(self, id):
        return self.model.load(id)

