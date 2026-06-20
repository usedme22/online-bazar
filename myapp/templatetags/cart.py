from django import template
from myapp.models import Product
from myapp.models import CheckoutProducts
from myapp.models import Checkout

register = template.Library()


@register.filter
def cartcolor(request, num):
    cart = request.session.get("cart", {})
    return cart[num][2] if cart else ""


@register.filter
def cartsize(request, num):
    cart = request.session.get("cart", {})
    return cart[num][3] if cart else ""


@register.filter
def cartQTY(request, num):
    cart = request.session.get("cart", {})
    return cart[num][1] if cart else ""   # qty index = 1


@register.filter
def carttotal(request, num):
    cart = request.session.get("cart", {})
    if not cart:
        return ""

    product_id = cart[num][0]
    qty = cart[num][1]

    try:
        p = Product.objects.get(id=int(product_id))
        return int(qty) * int(p.finalprice)
    except Product.DoesNotExist:
        return ""


@register.filter
def cartproductname(request, num):
    cart = request.session.get("cart", {})
    if not cart:
        return ""

    try:
        p = Product.objects.get(id=int(cart[num][0]))
        return p.name
    except Product.DoesNotExist:
        return ""


@register.filter
def cartproductimage(request, num):
    cart = request.session.get("cart", {})
    if not cart:
        return ""

    try:
        p = Product.objects.get(id=int(cart[num][0]))
        return p.pic1.url
    except Product.DoesNotExist:
        return ""


@register.filter
def finalprice(request, num):
    cart = request.session.get("cart", {})
    if not cart:
        return ""

    try:
        p = Product.objects.get(id=int(cart[num][0]))
        return p.finalprice
    except Product.DoesNotExist:
        return ""
    
@register.filter
def cartprice(request, key):
    cart = request.session.get("cart", {})
    if cart and key in cart:
        pid = cart[key][0]
        p = Product.objects.get(id=int(pid))
        return p.finalprice
    return 0

@register.filter("orderStatus")
def orderStatus(request,num):
    if(num==0):
        return "Cancelled"
    elif(num==1):
        return "Not Packed"
    elif(num==2):
        return "Packed"
    elif(num==3):
        return "Out For Delivery"
    else:
        return "Delivered"
    
@register.filter("paymentStatus")
def paymentStatus(request,num):
    if(num==1):
        return "Pending"
    else:
        return "Done"
    
@register.filter("paymentStatusCon")
def paymentStatusCon(request,num):
    if(num==1):
        return True
    else:
        return False
    
@register.filter(name='orderItem')
def orderItem(value, order_id):
    return CheckoutProducts.objects.filter(checkout_id=order_id)
