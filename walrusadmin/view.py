from flask.ext.admin.model import BaseModelView
import walrus
import wtforms

class ModelView(BaseModelView):
    def get_pk_value(self, model):
        return model.get_id()

    def scaffold_list_columns(self):
        columns = []

        for p in self.model._fields.keys():
            columns.append(p)

        return columns

    def scaffold_sortable_columns(self):
        return None

    def init_search(self):
        return None

    def scaffold_form(self):
        class MyForm(wtforms.Form):
            pass
            # TODO: Actually add fields to the form
        return MyForm

    def get_list(self, page, sort_field, sort_desc, search, filters,
        page_size=None):
        model_list = self.model.all()
        model_count = self.model.count()
        print model_count, model_list
        # TODO: Fix error and return the actual model list here!
        return model_count, []

    def get_one(self, id):
        return self.model.load(id)
