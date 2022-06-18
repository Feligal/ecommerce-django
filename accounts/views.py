


from django.contrib  import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from accounts.forms import RegistrationForm
from accounts.models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests

def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():            
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']            
            email = form.cleaned_data['email']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name,email=email, password=password, username=username)
            user.phone_number = phone_number
            user.save()
            #User activation 
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email =  EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            #messages.success(request, 'Thank you for registering with us. We have sent you a verification email  to your email address. Please verify it.')
            #return redirect('register')
            return redirect('/accounts/login/?command=verification&email='+ email)
    else:
        form = RegistrationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/register.html', context)
    

    
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))                
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()    
                             
                if is_cart_item_exists:   
                             
                    cart_item = CartItem.objects.filter(cart=cart)
                    productItems = []
                    for item in cart_item:
                        print(item.product)
                        productItems.append(item.product)
                    

                    existingProducts = []
                    id = []                                        
                    user_cart_items = CartItem.objects.filter(user=user) 
                                                                                                                       
                    for item in user_cart_items :                        
                        existingProducts.append(item.product)
                        print(item.product)
                        print(item.id)
                        id.append(item.id)
                   
                    for item in productItems:
                        if item in existingProducts:
                            index = existingProducts.index(item)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()                                                  
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()                                                                                                                        
            except:
                pass
            auth.login(request, user)
            messages.success(request,'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                #next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('g'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)                
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    
    return render(request, 'accounts/login.html')
    

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out.")
    return redirect("login")
    
    
def activate(request, uidb64, token):
    try:
        #decode the uidb64 to get the user primary id
        uid = urlsafe_base64_decode(uidb64).decode()
        #get user object
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated, you may now login')
        return redirect('login');
    else:
        messages.error(request, 'Sorry, invalid activation link.')
        return redirect('register')



    
@login_required(login_url='login')
def dashboard(request):
    context = {

    }
    return render(request,'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email = email).exists():
            user = Account.objects.get(email__iexact=email)

            #Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email =  EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist') 
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')
    


def resetpassword_validate(request, uidb64, token):
    try:
        #decode the uidb64 to get the user primary id
        uid = urlsafe_base64_decode(uidb64).decode()
        #get user object
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        #return redirect('/accounts/forgotPassword/?command=resetPassword&email='+ user.email)
        return redirect('resetPassword')
    else:
        messages.error(request, 'Sorry, this link has expired.')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            if uid is not None:
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset was successful, you can login with new password')
                return redirect('login')
            else:
                messages.error(request, 'Invalid reset token')    
                return redirect('resetPassword')    
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetPassword')    
    else:
        return render(request, 'accounts/resetPassword.html')