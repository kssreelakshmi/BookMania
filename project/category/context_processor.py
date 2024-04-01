from store.models import Attribute,AttributeValue
from category.models import Category

def category_list(request):
     category_list = Category.objects.filter(is_active=True)
     return dict(category_list=category_list)

     # def attribute_list(request):
     #     attribute_list = Attribute.objects.filter(is_active=True)
     #     print(attribute_list)
     #     return dict(attribute_list=attribute_list) 

def attribute_value_list(request):
     attribute_value_list = AttributeValue.objects.filter(is_active=True)
     attribute_content = {}
     # dictionary format
     # {
     #      bookcover: harcover, paperback,
     #      language: english, hindi, tamil, malayalam
     # }
     for i in attribute_value_list:
          if i.is_active:
               if i.attribute.attribute_name in attribute_content:
                    attribute_content[i.attribute.attribute_name].append(i.attribute_value)
               else:
                    attribute_content[i.attribute.attribute_name] = [i.attribute_value]
     print(attribute_content)
     return dict(attribute_content=attribute_content)