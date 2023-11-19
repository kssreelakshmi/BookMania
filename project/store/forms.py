from django import forms
from .models import Product,ProductVariant,Attribute,AttributeValue


class ProductForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_available'].widget.attrs['class'] = 'form-check-input'
        
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug',]
        
        
class ProductVariantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = ''
    
    
    
    class Meta:
        model = ProductVariant
        fields = '__all__'
        exclude = ['product','thumbnail_image', 'product_variant_slug','additionalimages']   
        

class CreateAttributeForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = ''    
    class Meta:
        model = Attribute
        fields = '__all__'
 
class CreateAttributeValueForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = ''
           
    class Meta:
        model = AttributeValue
        fields = '__all__'        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
         