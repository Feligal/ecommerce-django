from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        #fields = ['first_name', 'last_name', 'payment_method','phone','email','address_line_1','address_line_2', 'country', 'state','city','order_note','payment_method']        
        fields = ['payment_method']        