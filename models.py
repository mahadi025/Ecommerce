from mongoengine import Document, StringField, DateTimeField, IntField, FloatField, ReferenceField, BooleanField, DecimalField
from flask_admin.contrib.mongoengine import ModelView
from flask_admin.form import FileUploadField
from flask_login import UserMixin
from __init__ import *

__, admin = start()


@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=user_id)


class User(Document, UserMixin):
    username = StringField(required=True, unique=True)
    email = StringField(required=True)
    password = StringField(required=True)
    is_active = BooleanField(default=True)
    is_authenticated = BooleanField(default=True)
    is_anonymous = BooleanField(default=True)

    def __str__(self):
        return self.username


class UserView(ModelView):
    column_list = ('username', 'email')
    form_columns = ('username', 'email', 'password')


class Customer(Document):
    user = ReferenceField(
        User, unique=True, reverse_delete_rule=db.CASCADE, null=True, blank=True)
    name = StringField(null=True, blank=True,)
    email = StringField(required=True, unique=True)
    image = StringField(null=True, blank=True, default='DefaultProfilePic.jpg')
    phone = StringField(default="+880")

    def __str__(self):
        return self.name


class CustomerView(ModelView):
    column_searchable_list = ('name', 'email', 'phone')
    form_columns = ('user', 'name', 'email', 'image', 'phone')
    form_extra_fields = {
        'image': FileUploadField('Image',
                                 base_path='static/images',
                                 allowed_extensions=['jpg', 'png', 'jpeg'])
    }


class Product(Document):
    CATEGORY = (
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Both', 'Both'),
        ('Kid', 'Kid')
    )
    name = StringField(required=True, unique=True)
    price = FloatField(max_digits=5, decimal_places=2, required=True)
    image = StringField(default='DefaultProfilePic.jpg')
    category = StringField(required=True, choices=CATEGORY,)
    description = StringField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProductView(ModelView):
    column_list = ('name', 'price', 'category', 'description')
    form_columns = ('name', 'price', 'image', 'category', 'description')
    form_extra_fields = {
        'image': FileUploadField('Image',
                                 base_path='static/images',
                                 allowed_extensions=['jpg', 'png', 'jpeg'])
    }


class Order(Document):
    guest_user = StringField(blank=True, null=True)
    guest_user_email = StringField(blank=True, null=True)
    customer = ReferenceField(Customer, reverse_delete_rule=db.CASCADE)
    date_ordered = DateTimeField(auto_now_add=True)
    complete = BooleanField(default=False, null=True, blank=True)
    transaction_id = StringField(max_length=200, null=True, unique=True)

    def __str__(self):
        return str(self.transaction_id)


class OrderView(ModelView):
    column_list = ('customer', 'date_ordered', 'complete',
                   'guest_user', 'guest_user_email')
    form_columns = ('customer', 'date_ordered', 'complete',
                    'transaction_id', 'guest_user', 'guest_user_email')


class OrderItem(Document):
    product = ReferenceField(Product, reverse_delete_rule=db.CASCADE)
    order = ReferenceField(Order, reverse_delete_rule=db.CASCADE)
    quantity = IntField(null=True, blank=True, default=0)
    date_added = DateTimeField(auto_now_add=True)
    name = StringField(max_length=200, null=True)


class OrderItemView(ModelView):
    column_list = ('product', 'order', 'quantity')
    form_columns = ('product', 'order', 'quantity', 'date_added', 'name')


class ShippingAddress(Document):
    customer = ReferenceField(
        Customer, reverse_delete_rule=db.CASCADE, null=True, blank=True)
    guest_user = StringField(blank=True, null=True)
    guest_user_email = StringField(blank=True, null=True)
    order = ReferenceField(Order, reverse_delete_rule=db.CASCADE)
    address = StringField(required=True)
    city = StringField(required=True)
    date_added = DateTimeField(auto_now_add=True)


class ShippingAddressView(ModelView):
    column_list = ('customer', 'order', 'address',
                   'city', 'date_added', 'guest_user', 'guest_user_email')
    form_columns = ('customer', 'order', 'address',
                    'city', 'date_added', 'guest_user', 'guest_user_email')


admin.add_view(UserView(User))
admin.add_view(CustomerView(Customer))
admin.add_view(ProductView(Product))
admin.add_view(OrderView(Order))
admin.add_view(OrderItemView(OrderItem))
admin.add_view(ShippingAddressView(ShippingAddress))
