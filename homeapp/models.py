from pyexpat.errors import messages

from logapp.models import User
from django.db import models
from django.utils.text import slugify
from django.urls.base import reverse

from bookstore.settings import audio_storage
from django.db.models import Avg, Count
import random

from logapp.models import Address


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)
    # slug=models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('category_name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return '{}'.format(self.category_name)
    def get_url(self):
        return reverse('category', args=[self.slug])

class SubCategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    subcategory_name = models.CharField(max_length=50, unique=True)
    # slug = models.SlugField(max_length=50, unique=True)
    category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.CASCADE)
    def __str__(self):
        return self.subcategory_name

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=100)
    # slug = models.SlugField(max_length=50, unique=True)
    book_category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.PROTECT)
    book_quantity = models.BigIntegerField(default=0)
    book_price = models.BigIntegerField(default=0)
    book_oldprice = models.BigIntegerField(default=0)
    book_author = models.CharField(max_length=50)
    book_year = models.BigIntegerField(default=0)
    book_language = models.CharField(max_length=50)
    book_publisher = models.CharField(max_length=100)
    book_status = models.BooleanField(default=True)
    book_desc = models.TextField()
    img = models.ImageField(upload_to='pics')
    img2 = models.ImageField(upload_to='pics', default=0)

    class Meta:
        ordering = ('book_name',)
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
    def __str__(self):
        return '{}'.format(self.book_name)

    def get_url(self):
        return reverse('product', args=[self.slug])

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def search(cls, book_name, book_author):
        return cls.objects.filter(book_name__icontains=book_name, book_author__icontains=book_author)


# Create your models here.
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Book,on_delete=models.CASCADE)
    product_qty=models.IntegerField(default=1)
    price=models.DecimalField(max_digits=20,decimal_places=2,default=0)

    def get_product_price(self):
        price=[self.product.price]
        return sum(price)
class Whishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Book,on_delete=models.CASCADE)
#
# class Order(models.Model):
#     order_id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
#     payment_mode= models.CharField(max_length=100)
#     payment_id = models.CharField(max_length=100, null=True)
#     order_status=(
#         ('pending','pending'),
#         ('out for shipping','out for shipping'),
#         ('delivered','delivered')
#
#     )
#     status = models.CharField(max_length=100,choices=order_status,default='pending' )
#     tracking_no = models.CharField(max_length=100, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return '{}  {}'.format(self.order_id,self.user)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(blank=True,null=True)
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)


    def __str__(self):
        return str(self.user)
# class Order_item(models.Model):
#     orderitem_id = models.AutoField(primary_key=True)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     product = models.ForeignKey(Book, on_delete=models.CASCADE)
#     quantity = models.BigIntegerField(default=1)
#     price = models.DecimalField(max_digits=20, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return '{}  {}'.format(self.orderitem_id, self.product)
class OrderPlaced(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Received', 'Received'),
        ('Shipped', 'Shipped'),
        ('On The Way', 'On The Way'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),

    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # customer = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, default=0)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS, default='Pending')
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_boy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_delivered', null=True, blank=True)

    def total_cost(self):
        return self.quantity


    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if not self.pk and not self.otp:
            self.otp = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

class ReviewRating(models.Model):
    product = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.headline)
class BookTypes(models.Model):
    booktype_id = models.AutoField(primary_key=True)
    book_types = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return '{}'.format(self.book_types)


class eBooks(models.Model):
    book_id = models.AutoField(primary_key=True)
    ebook_name = models.CharField(max_length=100)
    book_category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.PROTECT)
    book_price = models.BigIntegerField(default=0)
    book_oldprice = models.BigIntegerField(default=0)
    book_author = models.CharField(max_length=50)
    book_year = models.BigIntegerField(default=0)
    book_language = models.CharField(max_length=50)
    book_publisher = models.CharField(max_length=100)
    book_status = models.BooleanField(default=True)
    book_desc = models.TextField()
    img = models.ImageField(upload_to='pics')
    img2 = models.ImageField(upload_to='pics', default=0)
    listening_length = models.DurationField(default="00:00:00", blank=True, null=True)
    narrator = models.CharField(max_length=50,blank=True, null=True)
    audibleRelease_date = models.DateTimeField(auto_now_add=True)
    book_type = models.ForeignKey(BookTypes, verbose_name="BookType", on_delete=models.PROTECT)
    book_audioFile = models.FileField(blank=True, null=True, storage=audio_storage)
    book_pdf = models.FileField(blank=True, null=True)
    book_flipbook = models.CharField(max_length=100 ,blank=True, null=True)
    def __str__(self):
        return '{}'.format(self.ebook_name)