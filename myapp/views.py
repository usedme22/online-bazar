from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Q
from .models import *
import os
from onlinebazar.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY
import razorpay
from django.conf import settings
from random import randint
from django.conf import settings
from django.core.mail import send_mail
from requests import session
# ---------------- HOME ----------------
def home(request):
    products = Product.objects.all().order_by('-id')
    if(request.method=="POST"):
        # try:
           email = request.POST.get("email")
           n = Newsletter()
           n.email=email
           n.save()
        # except:
            # pass
           return HttpResponseRedirect("/")
    return render(request, 'home.html', {"Product": products})

# ---------------- LOGIN ----------------
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)

            if user.is_superuser:
                return HttpResponseRedirect('/admin/')
            else:
                return HttpResponseRedirect('/profile/')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


# ---------------- LOGOUT ----------------
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == 'POST':
        actype = request.POST.get('actype')

        if actype == 'seller':
            u = Seller()
        else:
            u = Buyer()

        u.name = request.POST.get('name')
        u.username = request.POST.get('username')
        u.email = request.POST.get('email')
        u.phone = request.POST.get('phone')

        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if password == cpassword:
            try:
                user = User.objects.create_user(
                    username=u.username,
                    password=password,
                    email=u.email
                )
                user.save()
                u.save()
                return HttpResponseRedirect('/login/')
            except:
                messages.error(request, 'Username already taken')
        else:
            messages.error(request, 'Password mismatch')

    return render(request, 'signup.html')


# ---------------- PROFILE ----------------
@login_required(login_url='/login/')
def profile(request):
    user = request.user

    if user.is_superuser:
        return HttpResponseRedirect('/admin/')

    seller = Seller.objects.filter(username=user.username).first()

    if seller:
        products = Product.objects.filter(seller=seller).order_by('-id')
        return render(request, "sellerprofile.html", {"User": seller, "products": products})

    buyer = Buyer.objects.filter(username=user.username).first()

    if buyer:
        wishlist = Wishlist.objects.filter(buyer=buyer)
        orders = Checkout.objects.filter(buyer=buyer)
        return render(request, "buyerprofile.html", {
            "User": buyer,
            "Wishlist": wishlist,
            "orders": orders
        })

    messages.error(request, "Profile not found")
    return redirect('/signup/')


# ---------------- UPDATE PROFILE ----------------
@login_required(login_url='/login/')
def updateprofile(request):
    user = request.user

    if user.is_superuser:
        return HttpResponseRedirect('/admin/')

    try:
        user_obj = Seller.objects.get(username=user.username)
    except:
        user_obj = Buyer.objects.get(username=user.username)

    if request.method == "POST":
        user_obj.name = request.POST.get('name')
        user_obj.email = request.POST.get('email')
        user_obj.phone = request.POST.get('phone')
        user_obj.addressline1 = request.POST.get('addressline1')
        user_obj.addressline2 = request.POST.get('addressline2')
        user_obj.addressline3 = request.POST.get('addressline3')
        user_obj.pin = request.POST.get('pin')
        user_obj.city = request.POST.get('city')
        user_obj.state = request.POST.get('state')

        if request.FILES.get("pic"):
            if user_obj.pic and os.path.isfile(user_obj.pic.path):
                os.remove(user_obj.pic.path)
            user_obj.pic = request.FILES.get("pic")

        user_obj.save()
        return HttpResponseRedirect('/profile/')

    return render(request, 'updateprofile.html', {"User": user_obj})


# ---------------- ADD PRODUCT ----------------
@login_required(login_url='/login/')
def addProduct(request):
    if request.method == "POST":
        p = Product()

        p.name = request.POST.get('name')
        p.maincategory = Maincategory.objects.get(id=request.POST.get('maincategory'))
        p.subcategory = Subcategory.objects.get(id=request.POST.get('subcategory'))
        p.brand = Brand.objects.get(id=request.POST.get('brand'))
        p.stock = request.POST.get('stock')

        baseprice = request.POST.get('baseprice') or 0
        discount = request.POST.get('discount') or 0

        p.baseprice = int(baseprice)
        p.discount = int(discount)
        p.finalprice = p.baseprice - (p.baseprice * p.discount / 100)

        # FIXED SIZE + COLOR
        p.size = ",".join(request.POST.getlist("size"))
        p.color = ",".join(request.POST.getlist("color"))

        p.description = request.POST.get('description')

        p.pic1 = request.FILES.get('pic1')
        p.pic2 = request.FILES.get('pic2')
        p.pic3 = request.FILES.get('pic3')
        p.pic4 = request.FILES.get('pic4')

        try:
            p.seller = Seller.objects.get(username=request.user.username)
        except:
            return HttpResponseRedirect('/profile/')

        p.save()
        return HttpResponseRedirect('/profile/')

    return render(request, 'addProduct.html', {
        "Maincategory": Maincategory.objects.all(),
        "Subcategory": Subcategory.objects.all(),
        "Brand": Brand.objects.all()
    })

@login_required(login_url='/login/')
def editProduct(request, num):
    p = get_object_or_404(Product, id=num)

    seller = Seller.objects.get(username=request.user.username)

    if p.seller != seller:
        return HttpResponseRedirect('/profile/')

    if request.method == "POST":

        p.name = request.POST.get('name')

        p.maincategory = Maincategory.objects.get(
            id=request.POST.get('maincategory')
        )

        p.subcategory = Subcategory.objects.get(
            id=request.POST.get('subcategory')
        )

        p.brand = Brand.objects.get(
            id=request.POST.get('brand')
        )

        p.stock = request.POST.get('stock', 'In Stock')

        baseprice = request.POST.get('baseprice') or 0
        discount = request.POST.get('discount') or 0

        p.baseprice = int(baseprice)
        p.discount = int(discount)

        p.finalprice = p.baseprice - (
            p.baseprice * p.discount / 100
        )

        p.size = ",".join(request.POST.getlist("size"))
        p.color = ",".join(request.POST.getlist("color"))

        p.description = request.POST.get('description')

        for pic_field in ['pic1', 'pic2', 'pic3', 'pic4']:
            new_file = request.FILES.get(pic_field)

            if new_file:
                old_file = getattr(p, pic_field)

                if (
                    old_file and
                    getattr(old_file, "path", None) and
                    os.path.isfile(old_file.path)
                ):
                    os.remove(old_file.path)

                setattr(p, pic_field, new_file)

        p.save()
        return HttpResponseRedirect('/profile/')

    colors = [
        "Red", "Green", "Yellow", "Pink", "White",
        "Black", "Blue", "Brown", "SkyBlue",
        "Orange", "Navy", "Gray"
    ]

    sizes = [
        "XS", "S", "SM", "M", "ML",
        "L", "LXL", "XL", "XXL", "XXXL", "XXXXL"
    ]

    stocks = [
        "In Stock",
        "Out Of Stock"
    ]

    pics = [
        "pic1",
        "pic2",
        "pic3",
        "pic4"
    ]

    selected_colors = (
        p.color.split(",")
        if p.color else []
    )

    selected_sizes = (
        p.size.split(",")
        if p.size else []
    )

    return render(request, 'editProduct.html', {
        "Product": p,
        "Maincategory": Maincategory.objects.all(),
        "Subcategory": Subcategory.objects.all(),
        "Brand": Brand.objects.all(),
        "Colors": colors,
        "Sizes": sizes,
        "Stock": stocks,
        "Pics": pics,
        "selected_colors": selected_colors,
        "selected_sizes": selected_sizes,
    })

# ---------------- DELETE PRODUCT ----------------
@login_required(login_url='/login/')
def deleteProduct(request, num):
    try:
        p = Product.objects.get(id=num)
        seller = Seller.objects.get(username=request.user.username)

        if p.seller == seller:
            for pic_field in ['pic1', 'pic2', 'pic3', 'pic4']:
                file = getattr(p, pic_field)
                if file and getattr(file, "path", None) and os.path.isfile(file.path):
                    os.remove(file.path)

            p.delete()

        return HttpResponseRedirect('/profile/')
    except:
        return HttpResponseRedirect('/profile/')


# ---------------- SHOP ----------------
from django.db.models import Q

def shop(request, mc, sc, br):
    products = Product.objects.all()

    # Category filters
    if mc != "All":
        products = products.filter(maincategory__slug=mc)

    if sc != "All":
        products = products.filter(subcategory__slug=sc)

    if br != "All":
        products = products.filter(brand__slug=br)

    # Search filter
    if request.method == "POST":
        search = request.POST.get("search", "").strip()

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

    context = {
        "Product": products,
        "Maincategory": Maincategory.objects.all(),
        "Subcategory": Subcategory.objects.all(),
        "Brand": Brand.objects.all(),
        "mc": mc,
        "sc": sc,
        "br": br,
    }

    return render(request, "shop.html", context)

# ---------------- SINGLE PRODUCT ----------------
def singleProduct(request, num):
    p = get_object_or_404(Product, id=num)

    color = [c for c in p.color.split(",") if c]
    size = [s for s in p.size.split(",") if s]

    return render(request, 'singleProduct.html', {
        "Product": p,
        "Color": color,
        "Size": size
    })


# ---------------- WISHLIST ----------------
def wishlist(request, num):
    try:
        buyer = Buyer.objects.get(username=request.user.username)
        product = Product.objects.get(id=num)

        if not Wishlist.objects.filter(buyer=buyer, product=product).exists():
            Wishlist.objects.create(buyer=buyer, product=product)

        return HttpResponseRedirect("/profile/")
    except:
        return HttpResponseRedirect("/profile/")


@login_required(login_url='/login/')
def deletewishlist(request, num):
    buyer = Buyer.objects.get(username=request.user.username)
    w = Wishlist.objects.get(id=num, buyer=buyer)
    w.delete()
    return HttpResponseRedirect('/profile/')


# ---------------- CART ----------------

def addToCart(request):
    pid = request.POST.get('pid')
    color = request.POST.get('color')
    size = request.POST.get('size')

    cart = request.session.get("cart", {})
    key = f"{pid}-{color}-{size}"

    if key in cart:
        cart[key][1] += 1
    else:
        cart[key] = [pid, 1, color, size]

    request.session["cart"] = cart
    return HttpResponseRedirect("/cart/")



def cart(request):
    cart = request.session.get('cart', {})

    total = 0
    shipping = 0

    for v in cart.values():
        p = Product.objects.get(id=int(v[0]))
        total += p.finalprice * v[1]

    if total < 1000 and cart:
        shipping = 150

    return render(request, 'cart.html', {
        "Cart": cart,
        "Total": total,
        "shipping": shipping,
        "final": total + shipping
    })


def updatecart(request, id, num):
    cart = request.session.get("cart", {})

    if id in cart:

        # decrease
        if num == 0:
            if cart[id][1] > 1:
                cart[id][1] -= 1

        # increase
        elif num == 1:
            cart[id][1] += 1

    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")

def deletecart(request, id):
    cart = request.session.get("cart", {})
    cart.pop(id, None)
    request.session['cart'] = cart
    return HttpResponseRedirect("/cart/")

client = razorpay.Client(
    auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY)
)
@login_required(login_url='/login/')
def checkout(request):
    cart = request.session.get("cart", None)

    total = 0
    shipping = 0
    final = 0

    if cart:
        for values in cart.values():
            p = Product.objects.get(id=int(values[0]))
            total += p.finalprice * values[1]

        if len(cart.values()) >= 1 and total < 1000:
            shipping = 150

        final = total + shipping

    try:
        buyer = Buyer.objects.get(username=request.user.username)
    except Buyer.DoesNotExist:
        return HttpResponseRedirect('/profile/')

    if request.method == "POST":

        mode = request.POST.get('mode')

        check = Checkout()
        check.buyer = buyer
        check.total = total
        check.shipping = shipping
        check.final = final

        if mode == "COD":
            check.mode = "COD"
        else:
            check.mode = "Net Banking"

        check.save()

        for value in cart.values():
            p = Product.objects.get(id=int(value[0]))

            cp = CheckoutProducts()
            cp.name = p.name
            cp.pic = p.pic1.url
            cp.size = value[3]
            cp.color = value[2]
            cp.price = p.finalprice
            cp.qty = value[1]
            cp.total = p.finalprice * value[1]
            cp.checkout = check
            cp.save()

        if mode == "COD":
            request.session['cart'] = {}
            return HttpResponseRedirect('/confirmation/')

        return redirect('paynow', num=check.id)

    return render(
        request,
        "checkout.html",
        {
            "Cart": cart,
            "total": total,
            "shipping": shipping,
            "final": final,
            "User": buyer
        }
    )

@login_required(login_url='/login/')
def paynow(request, num):

    try:
        buyer = Buyer.objects.get(username=request.user.username)
    except Buyer.DoesNotExist:
        return HttpResponseRedirect('/profile/')

    try:
        check = Checkout.objects.get(id=num, buyer=buyer)
    except Checkout.DoesNotExist:
        return HttpResponse("Invalid Order")

    try:
        orderAmount = int(check.final * 100)

        paymentOrder = client.order.create({
            "amount": orderAmount,
            "currency": "INR",
            "payment_capture": 1
        })

        paymentId = paymentOrder['id']

    except Exception as e:
        return HttpResponse(f"Razorpay Error: {e}")

    return render(
        request,
        "pay.html",
        {
            "amount": orderAmount,
            "api_key": RAZORPAY_API_KEY,
            "order_id": paymentId,
            "User": buyer
        }
    )

def confirmation(request):
    return render(request,"confirmation.html")

def contact(request):
    if request.method == "POST":
        message = request.POST.get("message", "").strip()

        if not message:
            messages.error(request, "Message is required")
            return render(request, "contact.html")

        c = Contact()
        c.name = request.POST.get("name")
        c.email = request.POST.get("email")
        c.phone = request.POST.get("phone")
        c.subject = request.POST.get("subject")
        c.message = message
        c.save()
        subject = 'Your Query Has been Submitted : Team Online Bazar'
        message =  """
                        Thanks to Share your Query with us
                        Our Team will Contact You Soon
                        Team : Online Bazar
                        keep shopping with us
                        http://localhost:8000                    
                   """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [c.email, ]
        send_mail( subject, message, email_from, recipient_list )

        messages.success(
            request,
            "Your Query Has Been Submitted!!!! Our Team Will Contact You Soon"
        )

    return render(request, "contact.html")

@login_required(login_url='/login/')
def paymentSuccess(request,rppid,rpoid,rpsid):
    buyer = Buyer.objects.get(username=request.user)
    check = Checkout.objects.filter(buyer=buyer)
    check = check[::-1]
    check = check[0]
    check.paymentId=rppid
    check.orderId=rpoid
    check.paymentsignature=rpsid
    check.paymentstatus = 2
    check.save()
    return HttpResponseRedirect('/confirmation/')

def forgetUsername(request):
    if(request.method=="POST"):
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        if(user is not None):
            try:
                user = Buyer.objects.get(username=username)
            except:
                user = Seller.objects.get(username=username)
            num = randint(100000,999999)
            request.session['otp']=num
            request.session['user']=username
            subject = 'OTP for Password Reset : Team Online Bazar'
            message =  """
                            OTP : %d
                            Team : Online Bazar
                            keep shopping with us
                            http://localhost:8000                    
                    """%num
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list )
            return HttpResponseRedirect("/forget_otp/")
        else:
            messages.error(request,"User Name not Found")
    return render(request,"forget_username.html")


def forgetOTP(request):
    if(request.method=="POST"):
        otp = int(request.POST.get("otp"))
        sessionOTP = request.session.get('otp',None)
        if(otp==sessionOTP):
            return HttpResponseRedirect("/forget_password/")
        else:
            messages.error(request,"Invalid OTP")
    return render(request,"forget_otp.html")

def forgetPassword(request):
    if(request.method=="POST"):
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        if(password==cpassword):
            user = User.objects.get(username=request.session.get("user"))
            user.set_password(password)
            user.save()
            return HttpResponseRedirect("/login/")
        else:
            messages.error(request,"Password and Confirm Password Does't Matched")
    return render(request,"forget_password.html")


