from django import forms
from .models import Product,ProductVariant,Attribute,AttributeValue,AdditionalProductImages,Publication,Author,ReviewRating


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
        
class ProductImageForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-check'
            
        self.fields['is_active'].widget.attrs['class'] = ''
    
    class Meta:
        model = AdditionalProductImages
        fields = ('image','is_active')
        
class PublicationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
        for field_name, field in self.fields.items():
            if field_name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = 'form-check d-inline-block p-3'
           
    class Meta:
        model = Publication
        fields = '__all__'        
        

class AuthorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
        for field_name, field in self.fields.items():
            if field_name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = 'form-check d-inline-block p-3'
           
    class Meta:
        model = Author
        fields = '__all__'        

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']     
        
        
        
        
        
        
        
        
        
         