from django.contrib import admin

from orders.models import Order, OrderProduct, Payment


# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    readonly_fields=('user','payment','order_number','first_name','last_name','phone','payment_method','email','order_total','tax','id','is_ordered')
    list_display = ['order_number','full_name','phone','email','status','order_total','tax','ip','is_ordered', 'created_at']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','phone','email']
    list_per_page = 20
    inlines = [OrderProductInline]
    


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_method','user','amount_paid','status','created_at']
    search_fields = ['user']
    list_per_page = 20

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['product','quantity','product_price','order','payment','user','ordered']
    search_fields = ['user']
    list_per_page = 20


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct,OrderProductAdmin )