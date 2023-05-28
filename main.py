from mongoengine.errors import DoesNotExist
from flask import jsonify
import json
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from forms import *
from flask_login import current_user, login_user, login_required
import datetime
from utils import *
import os
from werkzeug.utils import secure_filename
from __init__ import *


app, __ = start()


@app.route('/register', methods=['GET', 'POST'])
def registration():
    if not 'logged_in' in session:
        form = UserRegistrationLoginForm()
        if request.method == 'POST':
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password1']
            confirm_password = request.form['password2']
            if password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('registration'))
            if User.objects(username=username) or User.objects(email=email):
                flash('Username or email already exists')
                return redirect(url_for('registration'))
            user = User(username=username, email=email,
                        password=generate_password_hash(password))
            customer = Customer(user=user, name=name, email=user.email)
            user.save()
            customer.image = 'DefaultProfilePic.jpg'
            customer.save()
            return redirect(url_for('login'))
        return render_template('registration.html', form=form)
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.objects(username=username).first()
        if user and check_password_hash(user['password'], password):
            login_user(user)
            session['logged_in'] = True
            user.is_active = True
            return redirect(url_for('home'))
        else:
            flash('Username or Password is incorrect')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/view_profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    customer = Customer.objects.get(user=current_user)
    return render_template('view_profile.html', customer=customer)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    customer = Customer.objects.get(user=current_user)
    current_image = customer.image
    form = CustomerEditForm(obj=customer)
    if request.method == "POST":
        form.populate_obj(customer)
        if form.image.data:
            image_file = form.image.data
            if image_file:
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'images', filename)
                image_file.save(image_path)
                customer.image = f'{filename}'
        else:
            customer.image = 'DefaultProfilePic.jpg'
        customer.save()
        print(current_image)
        flash('Profile Updated')
        return redirect(url_for('view_profile'))

    return render_template('edit_profile.html', customer=customer, form=form)


@app.route('/', methods=['GET', 'POST'])
def home():
    print('Current User: ', current_user)
    data = cart_data(request)
    cart_items = data['cart_items']
    print('Cart total: ', cart_items)
    return render_template('main.html', cart_items=cart_items, current_user=current_user)


@app.route('/store', methods=['GET', 'POST'])
def store():
    data = cart_data(request)
    cart_items = data['cart_items']
    products = Product.objects.order_by('category')
    return render_template('store.html', products=products, cart_items=cart_items)


@app.route('/view_product<string:pk>', methods=['GET', 'POST'])
def view_product(pk):
    product = Product.objects.get(id=pk)
    return render_template('view_product.html', product=product)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    data = cart_data(request)
    cart_items = data['cart_items']
    items = data['items']
    cart_total = data['cart_total']
    return render_template('cart.html', cart_items=cart_items, items=items, cart_total=cart_total)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    data = cart_data(request)
    cart_items = data['cart_items']
    items = data['items']
    cart_total = data['cart_total']
    store_url = url_for('store')
    return render_template('checkout.html', cart_items=cart_items, items=items, cart_total=cart_total, store_url=store_url)


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
    # product.save()
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
        order_items = OrderItem.objects(order=order)
        if current_user.is_active:
            for item in order_items:
                cart_total += (item.product.price -
                               item.product.price*0.1)*item.quantity
            if total == cart_total:
                order.complete = True
        else:
            for item in order_items:
                cart_total += item.product.price*item.quantity
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
        name = data['form']['name']
        email = data['form']['email']
        cookie_data = cookie_cart(request)
        items = cookie_data['items']
        # try:
        #     customer = Customer(email=email,name=name)
        #     customer.save()
        # except:
        #     customer = Customer.objects(email=email).first()
        order = Order(guest_user=name, guest_user_email=email ,complete=False)
        order.transaction_id = transaction_id
        order.date_ordered = datetime.datetime.now()
        order.complete = True
        order.save()
        cart_total = 0
        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            order_item = OrderItem(
                product=product, order=order, quantity=item['quantity'])
            order_item.save()
        shipping_address = ShippingAddress(guest_user=name, guest_user_email=email,order=order,
                                           address=data['shipping']['address'],
                                           city=data['shipping']['city'], date_added=datetime.datetime.now())
        shipping_address.save()
    return jsonify(message='Payment Complete')


if __name__ == '__main__':
    login_manager.init_app(app)
    app.run(host='127.0.0.1', port=5001)
