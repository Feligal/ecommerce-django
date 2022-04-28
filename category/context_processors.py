from carts.views import _cart_id
from  .models import Category
def menu_links(request):
    links = Category.objects.all()
    return dict(links = links)

