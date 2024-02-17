from store.models import Attribute,AttributeValue
from category.models import Category

def category_list(request):
     category_list = Category.objects.filter(is_active=True)
     return dict(category_list=category_list)

def attribute_list(request):
    attribute_list = Attribute.objects.filter(is_active=True)
    return dict(attribute_list=attribute_list) 

def attribute_value_list(request):
     attribute_value_list = AttributeValue.objects.filter(is_active=True)
     return dict(attribute_value_list=attribute_value_list) 