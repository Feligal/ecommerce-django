
from itertools import product
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
import datetime
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def payments(request):
    return render(request, 'orders/payments.html')


def order_complete(request):
    return render(request,'orders/order_complete.html')


# Create your views here.

def place_order(request, total = 0, quantity = 0):
    current_user = request.user
    #If the cart count is less than or equal to 0, then redirect back to shop
    
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
        
    if cart_count <= 0: 
        return redirect('store')
        
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (16 * total) / 100

    grand_total = total + tax
        
    if request.method == 'POST':        
        form = OrderForm(request.POST)  
                         
        if form.is_valid():                        
            #Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = current_user.first_name
            data.last_name = current_user.last_name
            data.phone = current_user.phone_number
            data.email = current_user.email
            data.address_line_1 = ""
            data.address_line_2 = ""
            data.country = ""
            data.state = ""
            data.city = ""
            data.order_note = ""
            data.order_total = grand_total
            data.tax = tax

            data.payment_method = form.cleaned_data['payment_method']

            data.ip = request.META.get('REMOTE_ADDR')
            
            data.save()

            #Generate order number
            yr = int(datetime.date.today().strftime('%Y')) #Getting the year part
            dt = int(datetime.date.today().strftime('%d')) #Getting the date
            mt = int(datetime.date.today().strftime('%m'))#Getting the month
            d = datetime.date(yr,mt,dt)

            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)            

            #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            method = form.cleaned_data['payment_method']
            if method == 'VISA':
                card_name = request.POST.get('card_name')                
                card_number = request.POST.get('card_number')
                expiration = request.POST.get('expiration')
                cvc = request.POST.get('cvc')
            if method == 'AIRTEL':
                phone = request.POST.get('phone')
                pin = request.POST.get('pin')
            
            if method == 'MTN':
                phone = request.POST.get('phone')
                pin = request.POST.get('pin')


            payment = Payment(
                user = request.user,
                payment_id = order_number,
                payment_method = method,
                amount_paid = grand_total,
                status = "SUCCESS"                
            )
            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            #Move the cart items to Order Product table
            cart_items = CartItem.objects.filter(user=request.user)            
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()
                
                #Reduce the quantity  of the sold Items

                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()
                
            #Clear the Cart
            CartItem.objects.filter(user = request.user).delete()

            #Send order received email to the customer
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_received_email.html', {
                'user': request.user,       
                'order': order         
            })
            to_email = request.user.email
            #send_email =  EmailMessage(mail_subject,message, to=[to_email])
            #send_email.send()
            send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [to_email],
                fail_silently= False
            )

            #Send order number and transaction id back to sendData method via JsonResponse
            """data = {
                'order_number': order_number,
                'transID' : payment.payment_id
            }
            return JsonResponse(data)"""

            try:
                order = Order.objects.get(order_number = order_number,is_ordered=True)
                ordered_products = OrderProduct.objects.filter(order_id = order.id)
                
                subtotal = 0
                for item in ordered_products:
                    subtotal += item.product_price * item.quantity

                context = {
                    'subtotal': subtotal,
                    'order':order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transId': payment.payment_id,
                    'payment':payment,
                }
                return render(request,'orders/order_complete.html',context)
            except(Payment.DoesNotExist, Order.DoesNotExist):
                return redirect('home')

            #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

           

            """context = {
                'payment_method': data.payment_method,
                'order': order,
                'cart_items': cart_items,
                'total':total,
                'tax':tax,
                'grand_total': grand_total
            }            
            return render(request, 'orders/payments.html', context)               """
    else:
        return redirect('checkout')
