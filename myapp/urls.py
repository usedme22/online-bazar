from django.urls import path, register_converter
from myapp import views
from .converters import SignedIntConverter

register_converter(SignedIntConverter, "sint")

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('profile/',views.profile,name='profile'),
    path('updateprofile/',views.updateprofile,name='updateprofile'),
    path('addProduct/',views.addProduct,name='addProduct'),
    path('editProduct/<int:num>/',views.editProduct,name='editProduct'),
    path('deleteProduct/<int:num>/',views.deleteProduct,name='deleteProduct'),
    path('logout/',views.logout,name='logout'),
    path('shop/<str:mc>/<str:sc>/<str:br>/',views.shop,name='shop'),
    path('singleProduct/<int:num>/',views.singleProduct,name='singleProduct'),
    path('wishlist/<int:num>/',views.wishlist,name='wishlist'),
    path('add-to-cart/',views.addToCart,name='add-to-cart'),
    path('cart/',views.cart,name='cart'),
    path("update-cart/<str:id>/<int:num>/", views.updatecart, name="update-cart"),
    path("deletecart/<str:id>/", views.deletecart, name="deletecart"),
    path("checkout/", views.checkout, name="checkout"),
    path('confirmation/',views.confirmation,name='confirmation'),
    path('deletewishlist/<int:num>/',views.deletewishlist,name='deletewishlist',),
    path('contact/',views.contact,name='contact'),
    path('paymentSuccess/<str:rppid>/<str:rpoid>/<str:rpsid>/',views.paymentSuccess,name='paymentSuccess'),
    path('paynow/<int:num>/',views.paynow,name='paynow'),
    path('forget_username/',views.forgetUsername,name='forget_username'),
    path('forget_otp/',views.forgetOTP,name='forget_otp'),
    path('forget_password/',views.forgetPassword,name='forget_password'),

]