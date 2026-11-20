from flask_admin import Admin, expose, BaseView, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from urllib3 import request
from wtforms.fields.numeric import FloatField

from eapp import app, db, dao
from eapp.models import Category, Product, UserRoleEnum, ReceiptDetails, Receipt
from flask_login import logout_user, current_user
from flask import redirect, render_template
from datetime import datetime
from flask import request

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.count_products_by_cate())

admin = Admin(app=app, name="E-commerce's Admin", index_view=MyAdminIndexView())

class AuthenticatedView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN

class ProductView(AuthenticatedView):
    column_list = ['id', 'name', 'price', 'category_id']
    column_searchable_list = ['name']
    can_export = True
    edit_modal = True
    column_editable_list = ['name']
    column_filters = ['id', 'name', 'price']
    form_overrides = {
        'price': FloatField
    }

class BaseAuthenticatedView(BaseView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class StatsView(BaseAuthenticatedView):
    @expose('/')
    def index(self):
        revenue_by_products = dao.cal_revenue_by_product(kw=request.args.get('kw'))

        y = request.args.get('year')
        if not y:
            y = datetime.now().year


        revenue_by_time = dao.cal_revenue_by_time(time=request.args.get('time', 'month'), year=y)
        return self.render('admin/stats.html', revenue_by_products=revenue_by_products, revenue_by_time=revenue_by_time)

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

admin.add_view(AuthenticatedView(Category, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(AuthenticatedView(Receipt, db.session))
admin.add_view(AuthenticatedView(ReceiptDetails, db.session))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))