from django.core.exceptions import ObjectDoesNotExist
from carts.models import Cart, CartItem
from carts.views import _cart_id


def counter(request):
    cart_counter = 0
    #Check if the url is for the admin
    if 'admin' in request.path:
        return {}
    else:        
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                cart_counter += cart_item.quantity                   
        except Cart.DoesNotExist:
            cart_counter = 0
    return dict(cart_counter = cart_counter)            