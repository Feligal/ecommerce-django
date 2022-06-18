from re import I
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from store.models import Product

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Create your views here.
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id = product_id)# get the product

    #If user authenticated
    if current_user.is_authenticated:        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:     
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            existing_product_list = []
            id = []
            for item in cart_item:
                existing_product_list.append(item.product)
                id.append(item.id)
            
            
            if product in existing_product_list:
               index = existing_product_list.index(product)
               item_id = id[index]
               item = CartItem.objects.get(product=product, id=item_id)
               item.quantity += 1
               item.save()
            else:
                item = CartItem.objects.create(
                    product=product,
                    quantity=1, 
                    user=current_user
                )            
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user
            )
            cart_item.save()    
        return redirect('cart') 
        
    else:
        #If the user is not authenticated
        try:
            cart = Cart.objects.get(cart_id= _cart_id(request))#get the cart using the cart_id present in the session
           
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
       
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:     
            cart_item = CartItem.objects.filter(product=product, cart=cart)     
            existing_product_list = []
            id = []
            for item in cart_item:
                existing_product_list.append(item.product)
                id.append(item.id)

            if product in existing_product_list:
               index = existing_product_list.index(product)
               item_id = id[index]
               item = CartItem.objects.get(product=product, id=item_id)
               item.quantity += 1
               item.save()
            else:
                item = CartItem.objects.create(
                    product = product,
                    quantity = 1, 
                    cart = cart
                )
                item.save()            
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
            cart_item.save()    
        return redirect('cart')        

def remove_cart(request, product_id):        
    current_user = request.user    
    product = get_object_or_404(Product, id=product_id)#get the product
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=current_user)#get the cart item
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()    
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))#get the cart using the cart_id present in the session
            cart_item = CartItem.objects.get(product=product, cart=cart)#get the cart item
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete() 
    except:
        pass    
    return redirect('cart')    


def remove_cart_item(request, product_id):
    current_user = request.user  
    product = get_object_or_404(Product, id=product_id)
    if current_user.is_authenticated:                
        cart_item = CartItem.objects.get(product=product, user=current_user)
        cart_item.delete()
    else:        
        cart = Cart.objects.get(cart_id = _cart_id(request))
        
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
    return redirect('cart')


def cart(request, total = 0 , quantity= 0 ,cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (16 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass # ignore and do nothing


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items':cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html', context)



@login_required(login_url='login')
def checkout(request,total = 0 , quantity= 0 ,cart_items = None):
    try:
        tax = 0
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (16 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass # ignore and do nothing
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items':cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }

    return render(request, 'store/checkout.html', context)