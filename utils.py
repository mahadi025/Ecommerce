import json
from models import *
from mongoengine.errors import DoesNotExist
from flask_login import current_user


def cookie_cart(request):
    items = []
    cart_total = 0
    cart_items = 0
    try:
        cart = json.loads(request.cookies['cart'])
    except:
        cart = {}

    print('Cart:', cart)

    for i in cart:
        try:
            if (cart[i]['quantity'] > 0):
                cart_items += cart[i]['quantity']
                product = Product.objects.get(id=i)
                if current_user.is_active:
                    cart_total += ((item.product.price -
                                    (item.product.price)*(0.1)))*cart[i]['quantity']
                    item = {
                        'product': {
                            'id': product.id,
                            'name': product.name,
                            'price': ((item.product.price -
                                       (item.product.price)*0.1)),
                            'image': product.image
                        },
                        'quantity': cart[i]['quantity'],
                        'cart_total': cart_total
                    }
                else:
                    cart_total += product.price*cart[i]['quantity']
                    item = {
                        'product': {
                            'id': product.id,
                            'name': product.name,
                            'price': product.price,
                            'image': product.image
                        },
                        'quantity': cart[i]['quantity'],
                        'cart_total': cart_total
                    }
                items.append(item)
        except DoesNotExist:
            pass
    return {'cart_items': cart_items, 'items': items, 'cart_total': cart_total}


def cart_data(request):
    if current_user.is_active:
        customer = Customer.objects.get(user=current_user)
        order = Order.objects(customer=customer, complete=False).first()
        items = OrderItem.objects(order=order)
        cart_total = 0
        cart_items = 0
        for item in items:
            if current_user.is_active:
                cart_total += ((item.product.price -
                                (item.product.price)*0.1))*item.quantity
            else:
                cart_total += item.product.price*item.quantity
            cart_items += item.quantity
    else:
        cookie_data = cookie_cart(request)
        cart_items = cookie_data['cart_items']
        items = cookie_data['items']
        cart_total = cookie_data['cart_total']
    return {'cart_items': cart_items, 'items': items, 'cart_total': cart_total}
