from cart.models import Cart, Cart_item
from category.models import Category
from cart.models import Cart,Cart_item
from .views import _cart_id


def admin_categories(request):
    categories = Category.objects.all()
    return dict(adm_categories = categories)

def counter(request):
    if 'admin' in request.path:
        return {}
    else:
        cart = Cart.objects.filter(cart_id = _cart_id(request))
        if request.user.is_authenticated:
            cartItems = Cart_item.objects.filter(user=request.user)
        else:    
            cartItems = Cart_item.objects.filter(cart=cart[:1])
        total = 0
        for cart_item in cartItems:
            total += cart_item.sub_total()
        tax = (total * 5) / 100
    
    return dict(cartItems = cartItems, total = total, tax = tax)