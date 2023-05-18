from audioop import reverse
from datetime import timezone

from django.shortcuts import render, redirect
from django.http import HttpResponse
#
# from .encryption_util import encrypt, decrypt
from .models import Book,Category,Payment, OrderPlaced,eBooks,BookTypes,ReviewRating
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Cart,Whishlist
from django.contrib import messages
from logapp.models import User,Address
from django.conf import settings
import razorpay
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf
import random
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# from importlib.metadata import files
# # from settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
# # Create your views here.

def index(request):
    count = Cart.objects.filter(user=request.user.id).count()
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    tblBook = Book.objects.all()

    # id=Book.book_id
    # book = Book.objects.filter( book_id=id)
    # average_review = book.averageReview()
    # context = {
    #     'book': tblBook,
    #
    #     'averageReview': average_review
    # }
    # Book.objects.values('book_id', 'book_name', 'book_category','book_quantity','book_price', 'book_oldprice','book_author','book_year','book_publisher','book_language', 'book_desc', '', 'img', 'user')
    category = Category.objects.all()
    cart = Cart.objects.all()
    # for i in tblBook:
    #     i['encrypt_key'] = encrypt(i['id'])
    #     i['id'] = i['id']


    return render(request,'index.html',{'datas':tblBook,'category':category,'cart':cart,'count':count,'w_count':w_count})
def ebook(request):
 return render(request,'E-Book.html')

def audiobooks(request):
     w_count = Whishlist.objects.filter(user=request.user.id).count()
     count = Cart.objects.filter(user=request.user.id).count()
     category = Category.objects.all()
     book = eBooks.objects.all()
     cart = Cart.objects.all()
     return render(request,'audiobooks.html',{'datas':book,'category':category,'cart':cart,'count':count,'w_count':w_count})

def ebooks(request):
    category = Category.objects.all()
    book = eBooks.objects.all()
    cart = Cart.objects.all()
    return render(request, 'audiobooks.html', {'datas': book, 'category': category, 'cart': cart})
@login_required(login_url='login')
def audiobook(request,id):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    rproduct = eBooks.objects.all()
    single = eBooks.objects.filter(book_id=id)
    cart = Cart.objects.all()
    category = Category.objects.all()
    return render(request, 'audiobook.html', {'result': single,'products':rproduct,'category':category,'cart':cart,'count':count,'w_count':w_count})

def product(request,id):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    products = Book.objects.all()
    # id = decrypt(id)
    single = Book.objects.filter(book_id=id)
    cart = Cart.objects.all()
    category = Category.objects.all()
    # orderproduct = OrderPlaced.objects.filter(user=request.user, is_ordered=True).exists()
    review = ReviewRating.objects.filter(product_id=id, status=True)
    book = get_object_or_404(Book, book_id=id)
    average_review = book.averageReview()
    category_id = book.book_category_id
    relatedbook = Book.objects.filter(book_category_id=category_id).exclude(book_id=id)

    context = {
        'book': book,
        'review_count': book.countReview(),
        'averageReview' : average_review
    }
    return render(request, 'product.html', {'context':context,'result': single,'products':products,'relatedbook':relatedbook,'category':category,'cart':cart,'count':count,'w_count':w_count,'review':review})


# def product(request,book_slug):
#     rproduct = Book.objects.all()
#     single = Book.objects.get(slug=book_slug)
#     cart = Cart.objects.all()
#     category = Category.objects.all()
#     return render(request, 'product.html', {'result': single,'products':rproduct,'category':category,'cart':cart})
#
def reviewss(request,id):
        if request.method == 'POST':
            try:
                reviews = ReviewRating.objects.get(user_id=request.user.id, product_id=id)
                headline = request.POST.get('headline')
                rating = request.POST.get('rating')
                review = request.POST.get('review')
                reviews.headline = headline
                reviews.rating = rating
                reviews.review = review
                reviews.save()
                messages.success(request, 'Thank you! Your review has been updated.')
                return redirect(request.META.get('HTTP_REFERER'))
            except ReviewRating.DoesNotExist:
                headline = request.POST.get('headline')
                rating = request.POST.get('rating')
                review = request.POST.get('review')
                data = ReviewRating()
                data.headline = headline
                data.rating = rating
                data.review = review
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = id
                data.user_id = request.user.id
                if OrderPlaced.objects.filter(user_id=request.user.id, product_id=id, is_ordered=True).exists():
                    data.save()
                    messages.success(request, 'Thank you! Your review has been submitted.')
                    return redirect(request.META.get('HTTP_REFERER'))
                else:
                    messages.warning(request, 'You can only review products that you have purchased.')
                    return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect('/')


def categorys(request,id):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    category = Category.objects.all()
    books = Book.objects.filter(reviewrating__rating__gte=4.0).annotate(avg_rating=Avg('reviewrating__rating')).order_by('avg_rating')
    if( Category.objects.filter(category_id=id)):
         book = Book.objects.filter(book_category_id=id)
    return render(request,'categorys.html',{'datas':book,'category':category,'books':books,'count':count,'w_count':w_count})
# def pricefilter(request,id):
#     category = Category.objects.all()
#     books = Book.objects.all()
#     if (Category.objects.filter(cid=id)):
#         book = Book.objects.filter(book_category_id=id)
#     return render(request, 'prize.html', {'datas': book, 'category': category, 'books': books})

# def category(request,category_slug):
#     catslug = Category.objects.get(slug=category_slug)
#     return render(request, 'categorys.html', {'catgry': catslug})
# def category(request):
#     if request.method == 'GET':
#         category_id = int(request.GET.get('category_id', default=1))
#         current_category = Category.objects.get(pk=category_id)
#         products = current_category.products.all()
#     return render(request, 'categorys.html',{'products': products})

def allproduct(request):
     w_count = Whishlist.objects.filter(user=request.user.id).count()
     count = Cart.objects.filter(user=request.user.id).count()
     category = Category.objects.all()
     book = Book.objects.all()
     # for i in book:
     #     i['encrypt_key'] = encrypt(i['id'])
     #     i['id'] = i['id']
     cart = Cart.objects.all()
     books = Book.objects.filter(reviewrating__rating__gte=4.0).annotate( avg_rating=Avg('reviewrating__rating')).order_by('avg_rating')

     return render(request,'all product.html',{'datas':book,'category':category,'cart':cart,'books':books,'count':count,'w_count':w_count})

def base(request,id):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    tblBook = Book.objects.all()
    category = Category.objects.filter(category_id=id)
    cart = Cart.objects.all()
    return render(request,'base1.html',{'datas':tblBook,'category':category,'cart':cart,'count':count,'w_count':w_count})


def searchbar(request):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    category = Category.objects.all()
    books = Book.objects.filter(reviewrating__rating__gte=4.0).annotate(
        avg_rating=Avg('reviewrating__rating')).order_by('avg_rating')
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            multiple_q = Q(Q(book_name__icontains=query) | Q(book_author__icontains=query))
            products = Book.objects.filter(multiple_q)
            return render(request, 'searchbar.html', {'datas':products,'category':category,'books':books,'count':count,'w_count':w_count})
        else:
            print("No information to show")
    return render(request, 'searchbar.html', {})


@login_required(login_url='login')
# def addcart(request,id):
#       user = request.user
#       item=Book.objects.get(book_id=id)
#       if item.book_quantity>0:
#             if Cart.objects.filter(user_id=user,product_id=item).exists():
#                   messages.success(request, 'Book Already in the cart ')
#                   return redirect(allproduct)
#             else:
#                   product_qty=1
#                   price=item.book_price * product_qty
#
#                   new_cart=Cart(user_id=user.id,product_id=item.book_id,product_qty=product_qty,price=price)
#                   new_cart.save()
#                   messages.success(request, 'Book added to the Cart ')
#                   return redirect(allproduct)

def addcart(request,id):
    user = request.user
    item = Book.objects.get(book_id=id)
    if item.book_quantity > 0:
        if Cart.objects.filter(user_id=user, product_id=item).exists():
            # If the book is already in the cart, increase the quantity by 1
            cart_item = Cart.objects.get(user_id=user, product_id=item)
            cart_item.product_qty += 1
            cart_item.price = item.book_price * cart_item.product_qty
            cart_item.save()

            messages.success(request, 'Book quantity updated in the cart ')
            return redirect(allproduct)
        else:
            product_qty = 1
            price = item.book_price * product_qty

            new_cart = Cart(user_id=user.id, product_id=item.book_id, product_qty=product_qty, price=price)
            new_cart.save()
            messages.success(request, 'Book added to the Cart ')
            return redirect(allproduct)


# Cart Quentity Plus Settings
def plusqty(request,id):
    cart=Cart.objects.filter(id=id)
    for cart in cart:
        if cart.product.book_quantity > cart.product_qty:
            cart.product_qty +=1
            cart.price=cart.product_qty * cart.product.book_price
            cart.save()
            return redirect('cart')
        # messages.success(request, 'Out of Stock')
        return redirect('cart')

# Cart Quentity minus Settings
def minusqty(request,id):
    cart=Cart.objects.filter(id=id)
    for cart in cart:
        if cart.product_qty > 1 :
            cart.product_qty -=1
            cart.price=cart.product_qty * cart.product.book_price
            cart.save()
            return redirect('cart')
        return redirect('cart')



# View Cart Page
@login_required(login_url='login')
def cart(request):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    user = request.user
    cart=Cart.objects.filter(user_id=user)
    totalitem=0
    total=0
    for i in cart:
        total += i.product.book_price * i.product_qty
        totalitem = len(cart)

    category=Category.objects.all()
    # subcategory=Subcategory.objects.all()
    return render(request,'cart.html',{'cart':cart,'total':total,'category':category,'totalitem':totalitem,'count':count,'w_count':w_count})

# Remove Items From Cart
def de_cart(request,id):
    Cart.objects.get(id=id).delete()
    return redirect(cart)

# add to wishlist
@login_required(login_url='login')
def add_wishlist(request,id):
    user = request.user
    item=Book.objects.get(book_id=id)
    if Whishlist.objects.filter( user_id =user,product_id=item).exists():
        messages.success(request, 'Book Already in the wishlist ')
        return redirect('allproduct')
    else:
            new_wishlist=Whishlist(user_id=user.id,product_id=item.book_id)
            new_wishlist.save()
            messages.success(request, 'Book added to the wishlist ')
            return redirect('allproduct')
    # messages.success(request, 'Sign in..!!')
    # return redirect(index)


#Wishlist View page
@login_required(login_url='login')
def view_wishlist(request):
        count = Cart.objects.filter(user=request.user.id).count()
        w_count = Whishlist.objects.filter(user=request.user.id).count()
        user = request.user
        wish=Whishlist.objects.filter(user_id=user)
        category=Category.objects.all()
        return render(request,"wishlist.html",{'wishlist':wish,'category':category,'w_count':w_count,'count':count})


# Remove Items From Wishlist
def de_wishlist(request,id):
    Whishlist.objects.get(id=id).delete()
    return redirect('view_wishlist')


def checkout(request):
    user = request.user
    product = Cart.objects.filter(user_id=user)
    total = 0
    for i in product:
        total += i.product.book_price * i.product_qty
        cart = Cart.objects.filter(user_id=user)
    category = Category.objects.all()
    tblBook = Book.objects.all()
    razoramount = total * 100
    print(razoramount)
    address = Address.objects.filter(user=request.user)
    print("address      ",address)

    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

    data = {
        "amount": total,
        "currency": "INR",
        "receipt": "order_rcptid_11"

    }
    payment_response = client.order.create(data=data)
    print(payment_response)
    order_id = payment_response['id']
    request.session['order_id'] = order_id
    order_status = payment_response['status']
    if order_status == 'created':
        payment = Payment(user=request.user,
                          amount=total,
                          razorpay_order_id=order_id,
                          razorpay_payment_status=order_status)
        payment.save()

    # context = {
    #     'razoramount': razoramount,
    #     'customer': customer,
    #     'total': total,
    #     'quantity': quantity,
    #     'cart_items': cart_items,
    #     'tax': tax,
    #     'grand_total': grand_total
    # }

    return render(request, 'checkout.html', {'datas': tblBook, 'category': category, 'product': cart, 'total':total,'razoramount':razoramount, 'address':address})
def send_order_confirmation_email(order):
    otp_code = order.otp
    user = order.user
    email_body = render_to_string('order_confirmation_email.html', {'order': order, 'otp_code': otp_code})

    message = render_to_string('order_confirmation_email.html', {
        'user': user,
        'otp_code': otp_code,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'email_body': email_body
    })

    send_mail(
        'Order Confirmation and OTP',
        message,
        'bookrakbook@gmail.com',
        [user.email],
        fail_silently=False,
    )

def payment_done(request):
    order_id = request.session['order_id']
    payment_id = request.GET.get('payment_id')
    print(payment_id)


    payment = Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    customer = Address.objects.filter(user=request.user)
    for i in customer:
        print(i.id)

    # id = request.POST.get('address')
    # print("customerdd              ", id)
    # selected_address = Address.objects.get(id=id)

    cart = Cart.objects.filter(user=request.user)
    for c in cart:
        otp_code = str(random.randint(100000, 999999))
        order = OrderPlaced(user=request.user,product=c.product, payment=payment, otp=otp_code, is_ordered=True)
        order.save()
        send_order_confirmation_email(order)
        c.product.book_quantity -= c.product_qty
        c.product.save()
        c.delete()

    return redirect('billview')
#
# def payment_done(request):
#     order_id = request.session['order_id']
#     payment_id = request.GET.get('payment_id')
#     print(payment_id)
#     customer = Address.objects.filter(user=request.user)
#     payment = Payment.objects.get(razorpay_order_id=order_id)
#     payment.paid = True
#     payment.razorpay_payment_id = payment_id
#     payment.save()
#     cart = Cart.objects.filter(user=request.user)
#     for c in cart:
#         otp_code = str(random.randint(100000, 999999))
#         order = OrderPlaced(user=request.user,product=c.product, payment=payment, otp=otp_code, is_ordered=True)
#         order.save()
#         send_order_confirmation_email(order)
#         c.product.book_quantity -= c.product_qty
#         c.product.save()
#         c.delete()
#
#     return redirect('billview')

def billview(request):
    count = Cart.objects.filter(user=request.user.id).count()
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    orders = OrderPlaced.objects.filter(
        user=request.user, is_ordered=True).order_by('ordered_date')
    return render(request,'bill_view.html',{ 'orders': orders,'w_count':w_count,'count':count})

@login_required(login_url='login')
def admin_profile(request):

    return render(request,'admin_profile.html')

@login_required(login_url='login')
def admin_index(request):
    user=request.user
    users = User.objects.all().count()
    book = Book.objects.all().count()
    ebook = eBooks.objects.all().count()
    review = ReviewRating.objects.all().count()
    order = OrderPlaced.objects.all().count()
    amount = OrderPlaced.objects.all()
    Revenue = 0
    for i in amount:
        Revenue += i.product.book_price
    # amount=OrderPlaced.objects.filter(amount=OrderPlaced.payment.amount)
    # Revenue = order * amount.payment.amount
    # Get the count of each ordered product by month
    order_count_by_product = OrderPlaced.objects.filter(is_ordered=True) \
        .values('product__book_name') \
        .annotate(count=Count('product'))

    # Create a list of traces for each product
    traces = []
    for count in order_count_by_product:
        product_name = count['product__book_name']
        product_count = count['count']
        traces.append(go.Bar(x=[product_name],
                             y=[product_count],
                             name=product_name))

    # Create the layout for the chart
    layout = go.Layout(title='Most Ordered Books',
                       xaxis=dict(title='Books'),
                       yaxis=dict(title='No: of Orders'))

    # Create the figure and render it as a div
    fig = go.Figure(data=traces, layout=layout)
    plot_div = plot(fig, output_type='div')

    order_count_by_product = OrderPlaced.objects.filter(is_ordered=True) \
        .values('product__book_name') \
        .annotate(count=Count('product'))

    # Create a list of traces for each product
    traces = []
    for count in order_count_by_product:
        product_name = count['product__book_name']
        product_count = count['count']
        traces.append(go.Scatter(x=[product_name],
                                 y=[product_count],
                                 mode='lines',
                                 name=product_name))

    # Create the layout for the chart
    layout = go.Layout(title='Most Ordered Products',
                       xaxis=dict(title='Product'),
                       yaxis=dict(title='Quantity'))

    # Create the figure and render it as a div
    fig = go.Figure(data=traces, layout=layout)
    plot_divs = plot(fig, output_type='div')

    return render(request,'admin_index.html',{'users':users,'book':book,'ebook':ebook,'review':review,'order':order,'Revenue':Revenue,'user':user,'plot_div':plot_div,'plot_divs':plot_divs})

@login_required(login_url='login')
def admin_base(request):
    return render(request, 'admin_base.html')

@login_required(login_url='login')
def admin_delboy(request):
    users = User.objects.filter(is_staff=True,is_superadmin=False)
    return render(request, 'admin_delboy.html',{'users':users})

@login_required(login_url='login')
def admin_users(request):
    users = User.objects.all()
    return render(request, 'admin_users.html',{'users':users})
import csv
def order_detailslog(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="order_details.csv"'
    writer = csv.writer(response)
    writer.writerow(['user', 'ordered_date','product'])
    order_details = OrderPlaced.objects.all().values_list('user', 'ordered_date','product')
    for i in order_details:
        writer.writerow(i)
    return response

@login_required(login_url='login')
def admin_uprofile(request,id):
    users = User.objects.get(id=id)
    return render(request, 'admin_uprofile.html',{'users':users})

@login_required(login_url='login')
def admin_dprofile(request,id):
    users = User.objects.get(id=id)
    if request.method == "POST":
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        user_id = User.objects.get(id=id)
        username = request.POST.get('username')
        hname = request.POST.get('hname')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        users = User.objects.get(id=id)
        users.first_name = first_name
        users.last_name = last_name
        users.phonenumber = phonenumber
        users.email = email
        users.city = city
        users.country = country
        users.state = state
        users.pincode = pincode
        users.username = username
        users.hname = hname

        users.save()
        messages.success(request, 'Profile Successfully Updated. ')

    return render(request, 'admin_dprofile.html',{'users':users})
def add_deliveryboy(request):
    if request.method == "POST":
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        hname = request.POST.get('hname')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        users = User(username=username,last_name=last_name,first_name=first_name,email=email,
                     phonenumber=phonenumber,hname=hname,country=country,state=state,city=city,pincode=pincode)
        users.is_active = True
        users.is_user = True
        users.is_staff=True
        users.save()
        messages.success(request, 'Delivery Boy Added. ')
        return redirect('admin_delboy')
    return render(request, 'add_deliveryboy.html')
def delete_dboy(request,id):
    users = User.objects.get(id=id)
    users.delete()
    messages.success(request, 'Delivery Boy Deleted. ')
    return redirect(admin_delboy)
def dboylastorder(request):
    user=User.objects.filter(is_staff=True,is_admin = False)
    for user in user:
        print(user.username)

    last_order = OrderPlaced.objects.filter(status='Delivered').order_by('-id').first()
    return render(request, 'dboylastordr.html',{'last_order': last_order,'user': user})
@login_required(login_url='login')
def admin_ebook(request):
    ebook = eBooks.objects.all()
    return render(request, 'admin_ebook.html', {'ebook': ebook})


@login_required(login_url='login')
def admin_ebookview(request,id):
    ebook = eBooks.objects.filter(book_id=id)
    return render(request, 'admin_ebookview.html',{'ebook':ebook})

@login_required(login_url='login')
def add_ebook(request):
    category = Category.objects.all()
    book_type = BookTypes.objects.all()
    if request.method == "POST":
        ebook_name= request.POST.get('ebook_name')
        category_id = request.POST.get('book_category')
        booktype_id = request.POST.get('book_types')
        book_category = Category.objects.get(category_id=category_id)
        book_types = BookTypes.objects.get(booktype_id=booktype_id)
        book_author = request.POST.get('book_author')
        book_year = request.POST.get('book_year')
        book_language = request.POST.get('book_language')
        book_publisher = request.POST.get('book_publisher')
        book_desc = request.POST.get('book_desc')
        img = request.FILES['img']
        img2 = request.FILES['img2']
        listening_length = request.POST.get('listening_length')
        narrator = request.POST.get('narrator')
        audibleRelease_date = request.POST.get('audibleRelease_date')
        book_pdf = request.FILES['book_pdf']
        book_flipbook = request.POST.get('book_flipbook')
        book = eBooks(ebook_name=ebook_name, book_category=book_category, book_author=book_author, book_year=book_year, book_language=book_language,
                     book_publisher=book_publisher, book_desc=book_desc, img = img, img2 = img2, listening_length=listening_length, narrator=narrator,
                     audibleRelease_date=audibleRelease_date, book_type=book_types, book_pdf = book_pdf ,book_flipbook = book_flipbook)
        book.save()
        messages.success(request, 'E-Book Added. ')
        return redirect(admin_ebook)
    return render(request, 'add_ebook.html',{'category':category,'book_type':book_type})

@login_required(login_url='login')
def deleteebook(request,id):
    item  = eBooks.objects.get(book_id=id)
    item.delete()
    messages.success(request, 'Book Deleted. ')
    return redirect(admin_ebook)

@login_required(login_url='login')
def ebookupdate(request,id):
    cat = Category.objects.all()
    if request.method == "POST":
        book_id = request.POST.get('book_id')
        ebook_name= request.POST.get('ebook_name')
        book_author = request.POST.get('book_author')
        book_year = request.POST.get('book_year')
        book_language = request.POST.get('book_language')
        book_publisher = request.POST.get('book_publisher')
        book_desc = request.POST.get('book_desc')
        narrator = request.POST.get('narrator')

        book = eBooks.objects.get(book_id=id)
        book.ebook_name = ebook_name
        book.book_author = book_author
        book.book_year = book_year
        book.book_language = book_language
        book.book_publisher = book_publisher
        book.book_desc = book_desc
        book.narrator = narrator

        book.save()
        messages.success(request, 'E-Book Updated. ')
    return redirect(admin_ebook)



@login_required(login_url='login')
def admin_category(request):
    cat = Category.objects.all()
    return render(request, 'admin_category.html',{'cat':cat})
def addcat (request):
    if request.method == "POST":
        cat = request.POST.get('cat')
        category = Category(category_name=cat)
        category.save()
        messages.success(request, 'Category Added. ')
        return redirect(admin_category)
def deletecat(request,id):
    item  = Category.objects.get(category_id=id)
    item.delete()
    messages.success(request, 'Category Deleted. ')
    return redirect(admin_category)
def editcat(request,id):
    if request.method == "POST":

        cat = request.POST.get('cat')
        value = Category.objects.get(category_id=id)
        value.category_name = cat
        value.save()
        messages.success(request, 'Category Updated. ')
    return redirect(admin_category)

@login_required(login_url='login')
def admin_book(request):
    book = Book.objects.all()
    for product in book:
        if product.book_quantity < 5:
            messages.warning(request, f'Stock for {product.book_name} is below 5')
    return render(request, 'admin_book.html',{'book':book})
def book_export( request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_details.csv"'
    writer = csv.writer(response)
    writer.writerow(['Usename', 'Phonenumber','Email'])
    user_details =  User.objects.all().values_list('first_name', 'phonenumber','email')
    for i in user_details:
        writer.writerow(i)
    return response
@login_required(login_url='login')
def admin_bookview(request,id):
    book = Book.objects.filter(book_id=id)
    category = Category.objects.all()
    return render(request, 'admin_bookview.html',{'book':book,'category':category})

@login_required(login_url='login')
def add_book(request):
    category = Category.objects.all()
    if request.method == "POST":
        book_name= request.POST.get('book_name')
        print("category_id:", book_name)
        category_id = request.POST.get('book_category')
        print("category_id:", category_id)
        book_category = Category.objects.get(category_id=category_id)
        book_quantity = request.POST.get('book_quantity')
        book_price = request.POST.get('book_price')
        book_oldprice = request.POST.get('book_oldprice')
        book_author = request.POST.get('book_author')
        book_year = request.POST.get('book_year')
        book_language = request.POST.get('book_language')
        book_publisher = request.POST.get('book_publisher')
        book_desc = request.POST.get('book_desc')
        img = request.FILES['img']
        img2 = request.FILES['img2']
        book = Book(book_name=book_name, book_category=book_category, book_quantity=book_quantity, book_price=book_price,
                     book_oldprice=book_oldprice, book_author=book_author, book_year=book_year, book_language=book_language,
                     book_publisher=book_publisher, book_desc=book_desc, img = img, img2 = img2)
        book.save()
        return redirect(admin_book)
    return render(request, 'add_book.html',{'category':category})

@login_required(login_url='login')
def deletebook(request,id):
    item  = Book.objects.get(book_id=id)
    item.delete()
    messages.success(request, 'Book Deleted. ')
    return redirect(admin_book)

@login_required(login_url='login')
def bookupdate(request,id):
    cat = Category.objects.all()
    if request.method == "POST":
        book_id = request.POST.get('book_id')
        book_name = request.POST.get('book_name')
        category_id = request.POST.get('book_category')
        book_category = Category.objects.get(category_id=category_id)
        book_quantity = request.POST.get('book_quantity')
        book_price = request.POST.get('book_price')
        book_oldprice = request.POST.get('book_oldprice')
        book_author = request.POST.get('book_author')
        book_year = request.POST.get('book_year')
        book_language = request.POST.get('book_language')
        book_publisher = request.POST.get('book_publisher')
        book_desc = request.POST.get('book_desc')
        # img = request.FILES['img']
        # img2 = request.FILES['img2']
        book = Book.objects.get(book_id=id)
        book.book_name = book_name
        book.book_category = book_category
        book.book_quantity = book_quantity
        book.book_price = book_price
        book.book_oldprice = book_oldprice
        book.book_authorock = book_author
        book.book_year = book_year
        book.book_language = book_language
        book.book_publisher = book_publisher
        book.book_desc = book_desc
        # book.img = img
        # book.img2 = img2
        book.save()
        messages.success(request, 'Category Updated. ')

    return redirect(admin_book)
from django.utils import timezone
@login_required(login_url='login')
def admin_orders(request):
    # order = OrderPlaced.objects.all()
    order = OrderPlaced.objects.order_by('-status')
    pending_orders = OrderPlaced.objects.filter(status='Pending')
    for orders in pending_orders:
        if (timezone.now() - orders.ordered_date).days > 10:
            messages.warning(request, f'Order of "{orders.product.book_name}"  Ordered by {orders.user.first_name} , Delivery is pending for more than 10 days  ')

    return render(request, 'admin_orders.html',{'order':order})

@login_required(login_url='login')
def admin_reviews(request):
    review = ReviewRating.objects.all()
    return render(request, 'admin_reviews.html',{'review':review})

def send_stock_alert(sender, **kwargs):
    product = kwargs['Book']
    message = f'The stock for {product.book_name} is below 5. Current stock: {product.book_quantity}'
    messages.warning( message)


def dboyindex(request):
    return render(request,'dboyindex.html')
def dboyblank(request):
    return render(request,'dboyblank.html')
# def dboy1(request):
#     orders = OrderPlaced.objects.exclude(status='Delivered')
#     context = {
#         'orders': orders,
#     }
#
#     return render(request,'dboy1.html',context)


from django.db.models import Q
def dboy1(request):
    # Get all the undelivered orders and sort them by ID
    orders = OrderPlaced.objects.exclude(status='Delivered').order_by('id')

    # Get the active delivery boys and sort them by ID
    delivery_boys = User.objects.filter(is_staff=True, is_admin=False, is_active=True).order_by('id')

    # Divide the orders equally among all the delivery boys
    num_delivery_boys = delivery_boys.count()
    orders_per_delivery_boy = orders.count() // num_delivery_boys
    remaining_orders = orders.count() % num_delivery_boys

    # Create a list of orders for each delivery boy
    order_lists = [[] for _ in range(num_delivery_boys)]
    index = 0
    for i, order in enumerate(orders):
        if index < num_delivery_boys:
            order_lists[index].append(order)
            index += 1
        else:
            index = 0
            order_lists[index].append(order)
            index += 1

    # Assign orders to delivery boys in a round-robin fashion
    order_index = 0
    for i, delivery_boy in enumerate(delivery_boys):
        orders_to_assign = orders_per_delivery_boy
        if i < remaining_orders:
            orders_to_assign += 1
        for order in order_lists[order_index][:orders_to_assign]:
            order.delivery_boy = delivery_boy
            order.save()
        order_index = (order_index + 1) % num_delivery_boys

    # Get the orders for the current delivery boy
    delivery_boy_orders = OrderPlaced.objects.filter(delivery_boy=request.user)

    context = {
        'orders': delivery_boy_orders,
    }

    return render(request, 'dboy1.html', context)


# def dboy1(request):
#     # Get all the undelivered orders
#     orders = OrderPlaced.objects.exclude(status='Delivered').order_by('id')
#
#     # Get the number of active delivery boys
#     delivery_boys = User.objects.filter(is_staff=True, is_admin=False, is_active=True)
#
#     # Divide the orders equally among all the delivery boys
#     num_delivery_boys = delivery_boys.count()
#     if num_delivery_boys > 0:
#         orders_per_delivery_boy = orders.count() // num_delivery_boys
#         remaining_orders = orders.count() % num_delivery_boys
#     else:
#         orders_per_delivery_boy = orders.count()
#         remaining_orders = 0
#
#     # Create a list of orders for each delivery boy
#     order_lists = [[] for _ in range(num_delivery_boys)]
#     index = 0
#     for i, order in enumerate(orders):
#         if index < num_delivery_boys:
#             order_lists[index].append(order)
#             index += 1
#         else:
#             index = 0
#             order_lists[index].append(order)
#             index += 1
#
#     # Assign delivery boy to orders in each order list and save them
#     for i, order_list in enumerate(order_lists):
#         delivery_boy = delivery_boys[i]
#         if i < remaining_orders:
#             orders_to_assign = orders_per_delivery_boy + 1
#         else:
#             orders_to_assign = orders_per_delivery_boy
#         for order in order_list[:orders_to_assign]:
#             order.delivery_boy = delivery_boy
#             order.save()
#
#     # Get the orders for the current delivery boy
#     delivery_boy_orders = OrderPlaced.objects.filter(delivery_boy=request.user)
#
#     context = {
#         'orders': delivery_boy_orders,
#     }
#
#     return render(request, 'dboy1.html', context)




# def dboy2(request, id):
#     order = OrderPlaced.objects.filter(id=id)
#     print('orders',order)
#     print('orders', OrderPlaced.otp)
#     if request.method == 'POST':
#         otp = request.POST.get('otp')
#         print('otp',otp)
#         if otp == OrderPlaced.otp:
#             order.status = 'Delivered'
#             order.save()
#             messages.success(request, 'Order delivered successfully')
#             return redirect('dboy2', id=id)
#         else:
#             messages.error(request, 'Invalid OTP')
#             return redirect('dboy2', id=id)
#     context = {
#         'orders': order,
#
#     }
#     return render(request, 'dboy2.html', context)
def dboy2(request, id):
    orders = OrderPlaced.objects.filter(id=id)
    order = get_object_or_404(OrderPlaced, id=id, status='Pending')
    print(order.status)
    print(order.otp)
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        print(entered_otp)
        if entered_otp == order.otp:
            order.status = 'Delivered'
            order.is_ordered = True
            order.save()
            print(order.status)
            return redirect(dboy3)
        else:
          messages.success(request, 'Invalid OTP. ')
    return render(request, 'dboy2.html', {'order': order,'orders': orders})
def dboy3(request):
    return render(request, 'dboy3.html')

def dboysetting(request):
    return render(request,'dboysetting.html')




import os
import tempfile
from io import BytesIO

import PyPDF2
import pyttsx3

from django.shortcuts import get_object_or_404, render
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import keyboard
from .models import eBooks
engine = pyttsx3.init()
# audio_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'audio'))
@login_required(login_url='login')
def pdf_to_audio(request, id):
    count = Cart.objects.filter(user=request.user.id).count()
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    global stop_flag
    ebook = get_object_or_404(eBooks, book_id=id)
    audio_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'audio'))
    if not ebook.book_pdf:
        return render(request, 'error.html', {'message': 'PDF not found'})

    # Check if the audio file already exists for this eBook
    if ebook.book_audioFile:
        audio_file_url = audio_storage.url(ebook.book_audioFile.name)
        return render(request, 'pdf_to_audio.html', {'audio_file_url': audio_file_url, 'count': count, 'w_count': w_count})

    # If the audio file doesn't exist, create it
    pdf_reader = PyPDF2.PdfReader(BytesIO(ebook.book_pdf.read()))
    num_pages = len(pdf_reader.pages)
    text = ''
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        engine.save_to_file(text, temp_file.name)
        print(os.path.exists(temp_file.name))
        temp_file.flush()
        os.fsync(temp_file.fileno())
        audio_filename = os.path.basename(temp_file.name)
        temp_file.close()
    with open(temp_file.name, 'rb') as f:
        audio_data = f.read()
    audio_content = ContentFile(audio_data)
    print(len(audio_data))

    # Save the audio file for this eBook
    ebook.book_audioFile.save(audio_filename, audio_content)

    # Render the template
    audio_file_url = audio_storage.url(ebook.book_audioFile.name)
    engine.stop()
    engine.say(text)
    print(audio_data)
    if stop_flag:
        engine.stop()
        stop_flag = False
    # engine.runAndWait()
    print('audio_file_url:', audio_file_url)
    return render(request, 'pdf_to_audio.html', {'audio_file_url': audio_file_url,'count':count,'w_count':w_count})



def run(request):
    count = Cart.objects.filter(user=request.user.id).count()
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    global stop_flag
    while not stop_flag:
        engine.runAndWait()
    return render(request, 'pdf_to_audio.html',{'count':count,'w_count':w_count})

def stop(request):
    global stop_flag
    stop_flag = True
    engine.setProperty('rate', 0)
    engine.stop()
    # engine.stop()
    return render(request, 'pdf_to_audio.html')
def pause(request):
    engine.pause()

    return redirect('pdf_to_audio')
def resume(request):
    engine.resume()
    return redirect('pdf_to_audio')
# import pyttsx3
# import spacy
# import en_core_web_sm
# # Load the English NLP model from spaCy
# nlp = spacy.load('en_core_web_sm')

# # Initialize the pyttsx3 text-to-speech engine
# engine = pyttsx3.init()

# def pdf_to_audio(request, id):
#     # Load the PDF file from the database
#     ebook = get_object_or_404(eBooks, book_id=id)
#     if not ebook.book_pdf:
#         return render(request, 'error.html', {'message': 'PDF not found'})

#     # Extract the text from the PDF using PyPDF2
#     pdf_reader = PyPDF2.PdfReader(BytesIO(ebook.book_pdf.read()))
#     num_pages = len(pdf_reader.pages)
#     text = ''
#     for page_num in range(num_pages):
#         page = pdf_reader.pages[page_num]
#         text += page.extract_text()

#     # Process the text using spaCy to extract named entities
#     doc = nlp(text)
#     entities = [ent.text for ent in doc.ents]

#     # Convert the entities to speech using pyttsx3
#     engine.setProperty('rate', 150)
#     for entity in entities:
#         engine.say(entity)

#     # Save the audio file to the book_audioFile field on the eBooks model
#     with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
#         engine.save_to_file(text, temp_file.name)
#         temp_file.flush()
#         os.fsync(temp_file.fileno())
#         audio_filename = os.path.basename(temp_file.name)
#     with open(temp_file.name, 'rb') as f:
#         audio_data = f.read()
#     audio_content = ContentFile(audio_data)
#     ebook.book_audioFile.save(audio_filename, audio_content)

#     # Get the URL of the saved audio file
#     audio_file_url = audio_storage.url(ebook.book_audioFile.name)
#     engine.say(text)
#     engine.runAndWait()
#     # Render the template with the audio file URL
#     return render(request, 'pdf_to_audio.html', {'audio_file_url': audio_file_url})

def get(request, id, *args, **kwargs, ):
        place = OrderPlaced.objects.get(id=id)
        date = place.payment.created_at

        orders = OrderPlaced.objects.filter(user_id=request.user.id, payment__created_at=date)
        total = 0
        for o in orders:
            total = total + (o.product.book_price * o.quantity)
        addrs = User.objects.get(id=request.user.id)

        data = {
            "total": total,
            "orders": orders,
            "shipping": addrs,

        }
        pdf = render_to_pdf('report.html', data)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # filename = "Report_for_%s.pdf" %(data['id'])
            filename = "Bill.pdf"

            content = "inline; filename= %s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Page Not Found")








import nltk
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from nltk.sentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
# sentiment_score = analyzer.polarity_scores(text)
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('vader_lexicon')

@method_decorator(csrf_exempt, name='dispatch')
class TextSummarizerView(View):

    template_name = 'summary.html'

    def get(self, request):
        return render(request, self.template_name)
    def post(self, request):
        count = Cart.objects.filter(user=request.user).count()
        w_count = Whishlist.objects.filter(user=request.user).count()
        input_text = request.POST.get('input_text', '')
        num_sentences = int(request.POST.get('num_sentences', 5))
        sentences = nltk.sent_tokenize(input_text)
        words = [nltk.word_tokenize(sentence) for sentence in sentences]
        words = [[word for word in sentence if word.isalnum()] for sentence in words]
        print(words)
        summaries = []
        for i in range(len(sentences)):
            score = nltk.sentiment.vader.SentimentIntensityAnalyzer().polarity_scores(sentences[i])['compound']
            print('score',score)
            summaries.append((sentences[i], score))
        summaries = sorted(summaries, key=lambda x: x[1], reverse=True)
        summaries = [summary[0] for summary in summaries[:num_sentences]]
        summary_text = ' '.join(summaries)
        return render(request, self.template_name, {'input_text': input_text, 'summary_text': summary_text, 'num_sentences': num_sentences,'count':count,'w_count':w_count})

from googletrans import Translator, LANGUAGES


def translation(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        source_language = request.POST.get('source_language')
        target_language = request.POST.get('target_language')
        # Check if the source and target languages are valid
        if source_language not in LANGUAGES or target_language not in LANGUAGES:
            context = {'error_message': 'Invalid source or target language'}
            return render(request, 'translation.html', context)
        try:
            # Create a Translator object and translate the text to the target language
            translator = Translator()
            translated_text = translator.translate(text, src=source_language, dest=target_language)
            # Render the translated text in the template
            context = {'translated_text': translated_text.text}
            return render(request, 'translation.html', context)
        except Exception as e:
            # Handle any exceptions and display an error message
            context = {'error_message': str(e)}
            return render(request, 'translation.html', context)
    else:
        # Render the initial form with dropdown menus for selecting the source and target languages
        source_language_choices = [(lang_code, lang_name) for lang_code, lang_name in LANGUAGES.items()]
        target_language_choices = [(lang_code, lang_name) for lang_code, lang_name in LANGUAGES.items()]
        context = {'source_language_choices': source_language_choices, 'target_language_choices': target_language_choices}
        return render(request, 'translation.html', context)



from django.shortcuts import render, get_object_or_404
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@login_required(login_url='login')
def book_recommendations(request):
    user = request.user
    # Get all books that the user has rated
    rated_books = ReviewRating.objects.filter(user=user, status=True)
    # rated_books = ReviewRating.objects.filter(status=True)
    # Get the IDs of the rated books

    rated_book_ids = [r.product.book_id for r in rated_books]
    # Get the books that the user has not rated
    unrated_books = Book.objects.exclude(book_id__in=rated_book_ids)
    if not unrated_books:
        return render(request, 'book_recommendations.html', {'recommended_books': []})
    # Get the text descriptions of the rated and unrated books
    rated_desc = [r.product.book_desc for r in rated_books]
    unrated_desc = [b.book_desc for b in unrated_books]
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    # Fit the vectorizer to the text descriptions
    vectorizer.fit(rated_desc + unrated_desc)
    # Transform the rated and unrated descriptions to TF-IDF vectors
    rated_vectors = vectorizer.transform(rated_desc)
    unrated_vectors = vectorizer.transform(unrated_desc)
    # Calculate the cosine similarity between the rated and unrated vectors
    similarity = cosine_similarity(rated_vectors, unrated_vectors)
    # Get the indices of the most similar unrated books for each rated book
    top_indices = similarity.argsort(axis=1)[:, ::-1][:, :2]
    # Get the book objects corresponding to the top indices
    recommended_books = []
    for i, book_indices in enumerate(top_indices):
        rated_book = get_object_or_404(Book, book_id=rated_book_ids[i])
        j = book_indices[0]
        unrated_book = unrated_books[int(j)]
        recommended_books.append((rated_book, unrated_book))
    recommended_books = np.array(recommended_books).tolist()  # Convert to Python list
    recommended_books = {i: {'rated_book': book_tuple[0], 'unrated_book': book_tuple[1]} for i, book_tuple in
                              enumerate(recommended_books)}
    return render(request, 'book_recommendations.html', {'recommended_books': recommended_books})





import nltk
nltk.download('vader_lexicon')
from django.shortcuts import render
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot

import seaborn as sns
import base64
import matplotlib.pyplot as plt
import io
import urllib
from django.db.models import Avg
from .models import ReviewRating
from django.shortcuts import render
from django.db.models import Avg
from .models import Book, ReviewRating
import plotly.graph_objs as go
from plotly.offline import plot


def review_analysis(request):
    # Load the review data from the database, filtering by status=True
    reviews = ReviewRating.objects.filter(status=True)

    # Convert the review data to a Pandas DataFrame
    review_data = pd.DataFrame(list(reviews.values()))

    # Tokenize the review text
    stop_words = stopwords.words('english')
    stemmer = SnowballStemmer('english')
    review_data['tokens'] = review_data['review'].apply(
        lambda x: [stemmer.stem(token.lower()) for token in word_tokenize(x) if token.lower() not in stop_words])

    # Calculate the sentiment score for each review using VADER
    sia = SentimentIntensityAnalyzer()
    review_data['sentiment_scores'] = review_data.apply(
        lambda x: sia.polarity_scores(x['review'])['compound'], axis=1)

    # Assign each review to a "positive" or "negative" category based on the sentiment score
    review_data['sentiment_category'] = review_data['sentiment_scores'].apply(
        lambda x: 'positive' if x >= 0.05 else 'negative')

    # Calculate the average sentiment score for each book
    book_sentiment = review_data.groupby(['product_id', 'sentiment_category'])['sentiment_scores'].mean().reset_index()
    book_data = pd.DataFrame(list(Book.objects.all().values()))
    book_data = book_data.merge(book_sentiment, left_on='book_id', right_on='product_id')

    # Separate the book data into positive and negative reviews
    positive_reviews = book_data[book_data['sentiment_category'] == 'positive']
    negative_reviews = book_data[book_data['sentiment_category'] == 'negative']

    # Sort the positive and negative reviews by sentiment score
    positive_reviews = positive_reviews.sort_values(by='sentiment_scores', ascending=False)
    negative_reviews = negative_reviews.sort_values(by='sentiment_scores', ascending=True)

    # Render the results
    positive_data = positive_reviews.to_dict('records')
    negative_data = negative_reviews.to_dict('records')

    plot_divs = []
    for data, title in zip([positive_data, negative_data], ['Positive Reviews', 'Negative Reviews']):
        book_names = [d['book_name'] for d in data]
        sentiment_scores = [d['sentiment_scores'] for d in data]
        fig = go.Figure([go.Bar(x=book_names, y=sentiment_scores)])

        fig.update_layout(
            title=title,
            xaxis_title="Book Names",
            yaxis_title="Sentiment Scores"
        )
        plot_div = plot(fig, output_type='div')
        plot_divs.append(plot_div)

    # create pie charts
    # for data, title in zip([positive_data, negative_data], ['Positive Reviews', 'Negative Reviews']):
    #     book_names = [d['book_name'] for d in data]
    #     sentiment_scores = [d['sentiment_scores'] for d in data]
    #     fig = go.Figure([go.Pie(labels=book_names, values=sentiment_scores)])
    #     fig.update_layout(title=title)
    #     plot_div = plot(fig, output_type='div')
    #     plot_divs.append(plot_div)

    context = {
        'book_data': book_data,
        'positive_data': positive_data,
        'negative_data': negative_data,
        'plot_divs': plot_divs,

    }
    return render(request, 'review_analysis.html', context)


# def review_analysis(request):
#     # Load the review data from the database, filtering by status=True
#     reviews = ReviewRating.objects.filter(status=True)
#     # Convert the review data to a Pandas DataFrame
#     review_data = pd.DataFrame(list(reviews.values()))
#     # Tokenize the review text
#     stop_words = stopwords.words('english')
#     stemmer = SnowballStemmer('english')
#     review_data['tokens'] = review_data['review'].apply(
#         lambda x: [stemmer.stem(token.lower()) for token in word_tokenize(x) if token.lower() not in stop_words])
#     # Calculate the sentiment score for each review using VADER
#     sia = SentimentIntensityAnalyzer()
#     review_data['sentiment_scores'] = review_data.apply(
#         lambda x: sia.polarity_scores(x['review'])['compound'] if x['rating'] >= 3 else -sia.polarity_scores(x['review'])['compound'], axis=1)
#     # Calculate the average sentiment score for each book
#     book_sentiment = review_data.groupby('product_id')['sentiment_scores'].mean().reset_index()
#     book_data = pd.DataFrame(list(Book.objects.all().values()))
#     book_data = book_data.merge(book_sentiment, left_on='book_id', right_on='product_id')
#     # print(book_data)
#     book_data = book_data.sort_values(by='sentiment_scores', ascending=False)
#     # print(book_data)
#     # Render the results
#     # book_data_dict = book_data.to_dict('list')
#     book_data = book_data.to_dict('records')
#     book_names = [d['book_name'] for d in book_data]
#     sentiment_scores = [d['sentiment_scores'] for d in book_data]
#     fig = go.Figure([go.Bar(x=book_names, y=sentiment_scores)])
#     plot_div = plot(fig, output_type='div')
#     fig = go.Figure(data=[go.Pie(labels=book_names, values=sentiment_scores)])
#     plot_divs = plot(fig, output_type='div')
#     context = {
#         'book_data': book_data,
#         'plot_div': plot_div,
#         'plot_divs': plot_divs
#     }
#     return render(request, 'review_analysis.html', context)







def rating_analysis(request):
    book_data = []
    for book in Book.objects.all():
        avg_review = book.reviewrating_set.filter(status=True).aggregate(Avg('rating'))['rating__avg']
        if avg_review is not None:
            book_data.append({
                'book_name': book.book_name,
                'avg_review': avg_review
            })
    book_names = [d['book_name'] for d in book_data]
    sentiment_scores = [d['avg_review'] for d in book_data]

    fig = go.Figure([go.Bar(x=book_names, y=sentiment_scores)])
    plot_div = plot(fig, output_type='div')
    fig = go.Figure(data=[go.Pie(labels=book_names, values=sentiment_scores)])
    plot_divs = plot(fig, output_type='div')
    context = {
        'book_data': book_data,
        'plot_div': plot_div,
        'plot_divs': plot_divs
    }
    return render(request, 'rating_analysis.html', context)
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
import plotly.graph_objs as go
from plotly.offline import plot
from .models import OrderPlaced

#///////////////
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import pytesseract
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from .models import Book
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
stop_words = set(stopwords.words('english'))
from django.db.models import Q


def book_search(request):
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    count = Cart.objects.filter(user=request.user.id).count()
    products = Book.objects.all()
    if request.method == 'POST' and request.FILES['book_cover']:
        uploaded_file = request.FILES['book_cover']
        # Extract text from the uploaded image
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        # Tokenize the text and remove stop words
        tokens = word_tokenize(text)
        print('tokens', tokens)
        tokens_without_stopwords = [token for token in tokens if not token in stop_words]
        # Identify the book title based on the extracted text
        book_title = None
        for token in tokens_without_stopwords:
            if Book.objects.filter(book_name__icontains=token).exists():
                book_title = token
                break
        # Search the database for the corresponding book
        if book_title:
            search_results = Book.objects.filter(Q(book_name__icontains=book_title) | Q(book_author__icontains=book_title))
            print('search_results',search_results)
            # Render the search results template with the search results
            return render(request, 'image_search.html', {'search_results': search_results,'w_count': w_count,'count': count,'products': products})
        else:
            messages.warning(request, 'No matching book found')
            return render(request, 'image_search.html')

    return render(request, 'image_search.html')

