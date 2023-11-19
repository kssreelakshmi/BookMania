from category.models import Category

def admin_categories(request):
    categories = Category.objects.all()
    return dict(adm_categories = categories)