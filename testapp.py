from flask import Flask
import walrus
from walrus.tusks.rlite import WalrusLite

from flask.ext.admin import Admin
from walrusadmin import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = '1'
app.config['CSRF_ENABLED'] = False
app.config['DEBUG'] = True

db = WalrusLite(':memory:')
admin = Admin(app)

class User(walrus.Model):
    database = db
    username = walrus.TextField(primary_key=True)
    password = walrus.TextField()
    is_active = walrus.BooleanField(default=True)
    first_name = walrus.TextField()
    last_name = walrus.TextField()
    email = walrus.TextField()
    addresses = walrus.HashField()

class UserAdmin(ModelView):
    pass

admin.add_view(UserAdmin(User))

def create_test_data():
    u = User()
    u.username='pp27'
    u.password='pass'
    u.email='pp27@a2b.in'
    u.first_name='Paruppu'
    u.last_name='Podi'
    u.save()
    u2 = User()
    u2.username='spapdi'
    u2.password='pass'
    u2.email = 'sone@pap.de'
    u2.first_name='Sone'
    u2.last_name='Papdi'
    u2.save()

if __name__ == '__main__':
    create_test_data()
    app.run()
