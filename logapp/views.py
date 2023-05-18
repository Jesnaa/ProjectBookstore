
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User, auth, models
from .models import User,Address
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail


from homeapp.models import OrderPlaced,Payment,Cart,Whishlist


def profile(request):
    count = Cart.objects.filter(user=request.user.id).count()
    w_count = Whishlist.objects.filter(user=request.user.id).count()
    orders = OrderPlaced.objects.filter(
        user=request.user, is_ordered=True).order_by('ordered_date')
    address= Address.objects.filter(user=request.user.id)
    return render(request,'profile.html', { 'orders': orders,'count':count,'w_count':w_count,'address':addressf})

def index(request):
    return render(request,'index.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['email']
        phonenumber = request.POST.get('phonenumber')
        hname=request.POST['hname']
        country = request.POST['country']
        state = request.POST['state']
        city = request.POST['city']
        pincode = request.POST['pincode']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        password = request.POST.get('password')

        if password == cpassword:

            if User.objects.filter(phonenumber=phonenumber).exists():
                messages.info(request, 'phonenumber already taken')
                return render(request, 'reg base.html')
            if User.objects.filter(email=email).exists():
                messages.info(request, 'email already taken')
                return render(request, 'reg base.html')

            else:
                user = User.objects.create_user(username=username, first_name=first_name,
                                                last_name=last_name, email=email,
                                                phonenumber=phonenumber,hname=hname,country=country, state=state,
                                                city=city, pincode=pincode, password=password)
                user.is_user = True
                user.save()
                address = Address(user=user, hname=hname, country=country, state=state, city=city, pincode=pincode)
                address.save()
                # if user.hname and user.country and user.state and user.city and user.pincode:
                #     address = Address(user=user, hname=user.hname, country=user.country, state=user.state,
                #                       city=user.city, pincode=user.pincode)
                #     address.save()

                messages.success(request, 'Please verify your email for login!')

                current_site = get_current_site(request)
                message = render_to_string('account_verification_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                send_mail(
                    'Please activate your account',
                    message,
                    'bookrakbook@gmail.com',
                    [email],
                    fail_silently=False,
                )

                return redirect('login')
                # return redirect('/login/?command=verification&email=' + email)

                # login = tbl_userLogin(username=username, password=password)
                # login.save()
                # return redirect('login')
        else:
            messages.info(request, 'password is not matching')
            print('password is not matching')
            return redirect('reg base.html')
    else:
        return render(request, 'reg base.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        user = auth.authenticate(email=email, password=password)
        print(user)

        if user is not None:
            auth.login(request, user)
            # save email in session
            request.session['email'] = email
            if user.is_admin:
                return redirect('admin_index')

            if user.is_staff:
                return redirect('dboy1')

            else:
                return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('/login/login/login/register')
    return render(request, 'login.html')


# @login_required
def changepassword(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = User.objects.get(email__exact=request.user.email)
        success = user.check_password(current_password)
        if success:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password updated successfully.Login Now')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('changepassword')
    return render(request, 'changepassword.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Reset password email

            current_site = get_current_site(request)
            message = render_to_string('ResetPassword_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(
                'Please activate your account',
                message,
                'bookrakbook@gmail.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'Forgot_Password.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'ResetPassword.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')



def profile_update(request):
    if request.method == "POST":

        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        user_id = request.user.id
        username = request.POST.get('username')
        hname = request.POST.get('hname')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.phonenumber = phonenumber
        user.email = email
        user.city = city
        user.country = country
        user.state = state
        user.pincode = pincode
        user.username = username
        user.hname = hname

        user.save()

        messages.success(request,'Profile Are Successfully Updated. ')
        return redirect('profile')


def add_address(request):
    if request.method == "POST":
        hname = request.POST.get('hname')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        # address = Address.objects.get(user_id=request.user.id)
        address = Address(user=request.user,hname = hname,city = city,state = state,country = country,pincode = pincode)

        address.save()

        messages.success(request,'Address Added  Successfully. ')
        return redirect('profile')
