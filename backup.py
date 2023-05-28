from mongoengine.errors import DoesNotExist
from flask import jsonify
import json
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from forms import *
from flask_login import current_user, login_user
import datetime


app = start()
csrf = CSRFProtect(app)


@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = UserRegistrationLoginForm()
    if request.method == 'POST':
        name = request.form['Name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password1']
        confirm_password = request.form['password2']
        if password != confirm_password:
            return 'Passwords do not match'
        if User.objects(username=username) or User.objects(email=email):
            return 'Username or email already exists'
        user = User(username=username, email=email,
                    password=generate_password_hash(password))
        customer = Customer(user=user, name=name, email=user.email)
        user.save()
        customer.save()
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.objects(username=username).first()
        if user and check_password_hash(user['password'], password):
            login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
def home():
    print('Current User: ', current_user)
    if current_user.is_active:
        customer = Customer.objects.get(user=current_user)
        order = Order.objects(customer=customer, complete=False).first()
        items = OrderItem.objects(order=order)
        cart_total = 0
        cart_items = 0
        for item in items:
            cart_total += item.product.price*item.quantity
            cart_items += item.quantity
    else:
        items = []
        cart_total = 0
        cart_items = 0
    return render_template('main.html', **locals())


@app.route('/store', methods=['GET', 'POST'])
def store():
    if current_user.is_active:
        customer = Customer.objects.get(user=current_user)
        order = Order.objects(customer=customer, complete=False).first()
        items = OrderItem.objects(order=order)
        cart_total = 0
        cart_items = 0
        for item in items:
            cart_total += item.product.price*item.quantity
            cart_items += item.quantity
    else:
        items = []
        try:
            cart = json.loads(request.cookies['cart'])
        except:
            cart = {}
        print('Cart:', cart)
        cart_total = 0
        cart_items = 0

        for i in cart:
            try:
                cart_items += cart[i]['quantity']
                product = Product.objects.get(id=i)
                cart_total += product.price*cart[i]['quantity']
                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'image': product.image
                    },
                    'quantity': cart[i]['quantity']
                }
                items.append(item)
            except:
                pass
    products = Product.objects.all()
    return render_template('store.html', **locals())


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if current_user.is_active:
        customer = Customer.objects.get(user=current_user)
        order = Order.objects(customer=customer, complete=False).first()
        items = OrderItem.objects(order=order)
        cart_total = 0
        cart_items = 0
        for item in items:
            cart_total += item.product.price*item.quantity
            cart_items += item.quantity
    else:
        items = []
        try:
            cart = json.loads(request.cookies['cart'])
        except:
            cart = {}
        print('Cart:', cart)
        cart_total = 0
        cart_items = 0

        for i in cart:
            try:
                cart_items += cart[i]['quantity']
                product = Product.objects.get(id=i)
                cart_total += product.price*cart[i]['quantity']
                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'image': product.image
                    },
                    'quantity': cart[i]['quantity']
                }
                items.append(item)
            except:
                pass
    return render_template('cart.html', **locals())


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if current_user.is_active:
        customer = Customer.objects.get(user=current_user)
        order = Order.objects(customer=customer, complete=False).first()
        items = OrderItem.objects(order=order)
        cart_total = 0
        cart_items = 0
        for item in items:
            cart_total += item.product.price*item.quantity
            cart_items += item.quantity
    else:
        items = []
        try:
            cart = json.loads(request.cookies['cart'])
        except:
            cart = {}
        print('Cart:', cart)
        cart_total = 0
        cart_items = 0

        for i in cart:
            try:
                cart_items += cart[i]['quantity']
                product = Product.objects.get(id=i)
                cart_total += product.price*cart[i]['quantity']
                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'image': product.image
                    },
                    'quantity': cart[i]['quantity']
                }
                items.append(item)
            except:
                pass
    store_url = url_for('store')
    return render_template('checkout.html', **locals())


@app.route('/update_item/', methods=['POST'])
def update_item():
    data = json.loads(request.data)
    product_id = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', product_id)

    customer = Customer.objects.get(user=current_user)
    product = Product.objects.get(id=product_id)

    try:
        order = Order.objects.get(customer=customer, complete=False)
    except DoesNotExist:
        order = Order(customer=customer, complete=False)
        order.save()

    try:
        order_item = OrderItem.objects.get(order=order, product=product)
    except DoesNotExist:
        order_item = OrderItem(order=order, product=product)
        order_item.quantity = 0

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return jsonify(message='Item was added')


@app.route('/process_order/', methods=['POST'])
def process_order():
    data = json.loads(request.data)
    transaction_id = str(datetime.datetime.now().timestamp())
    if current_user.is_active:
        customer = Customer.objects.get(user=current_user)
        try:
            order = Order.objects.get(customer=customer, complete=False)
        except DoesNotExist:
            order = Order(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        cart_total = 0
        items = OrderItem.objects(order=order)
        for item in items:
            cart_total += item.product.price*item.quantity
        print(total)
        print(cart_total)
        if total == cart_total:
            order.complete = True
        order.date_ordered = datetime.datetime.now()
        order.save()

        shipping_address = ShippingAddress(customer=customer, order=order,
                                           address=data['shipping']['address'],
                                           city=data['shipping']['city'], date_added=datetime.datetime.now())
        shipping_address.save()
    else:
        print('User is not logged in')
    return jsonify(message='Payment Complete')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
