from django.db import models
from django.utils.text import slugify

class Maincategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Seller(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"

class Seller(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    username=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    phone=models.CharField(max_length=50)
    addressline1=models.CharField(max_length=100,default=None,null=True,blank=True)
    addressline2=models.CharField(max_length=100,default=None,null=True,blank=True)
    addressline3=models.CharField(max_length=100,default=None,null=True,blank=True)
    pin=models.CharField(max_length=50,default=None,null=True,blank=True)
    city=models.CharField(max_length=50,default=None,null=True,blank=True)
    state=models.CharField(max_length=50,default=None,null=True,blank=True)
    pic=models.FileField(upload_to="images",default="no_user.png",null=True,blank=True)

    def __str__(self):
        return f"{self.name}"
    
class Product(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    maincategory=models.ForeignKey(Maincategory,on_delete=models.CASCADE)
    subcategory=models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
    seller=models.ForeignKey(Seller,on_delete=models.CASCADE,default=None)
    baseprice=models.IntegerField()
    discount=models.IntegerField()
    finalprice=models.IntegerField()
    size=models.CharField(max_length=100,null=True, blank=True)
    color = models.CharField(max_length=100,null=True, blank=True)
    description=models.TextField()
    stock=models.CharField(max_length=20,default="In stock")
    pic1=models.ImageField(upload_to="images",default="no_image.png",null=True,blank=True)
    pic2=models.ImageField(upload_to="images",default="no_image.png",null=True,blank=True)
    pic3=models.ImageField(upload_to="images",default="no_image.png",null=True,blank=True)
    pic4=models.ImageField(upload_to="images",default="no_image.png",null=True,blank=True)

    def __str__(self):
        return f"{self.name}"
    
class Buyer(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    username=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    phone=models.CharField(max_length=15)
    addressline1=models.CharField(max_length=100,default=None,null=True,blank=True)
    addressline2=models.CharField(max_length=100,default=None,null=True,blank=True)
    addressline3=models.CharField(max_length=100,default=None,null=True,blank=True)
    pin=models.CharField(max_length=50,default=None,null=True,blank=True)
    city=models.CharField(max_length=50,default=None,null=True,blank=True)
    state=models.CharField(max_length=50,default=None,null=True,blank=True)
    pic=models.FileField(upload_to="images",default="no_user.png",null=True,blank=True)

    def __str__(self):
        return f"{self.name}"
    
class Wishlist(models.Model):
    id=models.AutoField(primary_key=True)
    buyer=models.ForeignKey(Buyer,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} {self.buyer.username} {self.product}"

from django.db import models
from myapp.models import Buyer   # apne Buyer model ka correct import

# choices
ORDER_STATUS = (
    (0, "Cancel"),
    (1, "Not Packed"),
    (2, "Packed"),
    (3, "Out for Delivery"),
    (4, "Delivered"),
)

PAYMENT_STATUS = (
    (1, "Pending"),
    (2, "Done"),
)


class Checkout(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    shipping = models.IntegerField()
    final = models.IntegerField()
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    mode = models.CharField(max_length=20,default="COD")
    orderstatus = models.IntegerField(choices=ORDER_STATUS, default=1)
    paymentstatus = models.IntegerField(choices=PAYMENT_STATUS, default=1)
    rppid = models.CharField(max_length=50, default="", null=True, blank=True)
    rpoid = models.CharField(max_length=50, default="", null=True, blank=True)
    rpsid = models.CharField(max_length=50, default="", null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} {self.buyer.username}"
    
class CheckoutProducts(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    price = models.IntegerField()
    qty = models.IntegerField()
    total = models.IntegerField()
    pic = models.CharField(max_length=200)
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE)

    def __str__(self):
        return f"Product: {self.name} | Checkout ID: {self.checkout.id}"
    
class Newsletter(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50,unique=True)

    def __str__(self):
        return self.email

contactStatusChoice = ((1,"Active",),(2,"Done"))
class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    subject = models.TextField()
    message = models.TextField()
    status = models.IntegerField(choices=contactStatusChoice,default=1)

    def __str__(self):
        return str(self.id)+" "+self.email+" "+self.subject
