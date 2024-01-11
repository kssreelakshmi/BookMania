from django import forms
from accounts.models import Account
from accounts.models import Addresses
from django.contrib.auth.forms import PasswordResetForm


class UserSignupForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'first_name',
            'last_name',
            'username',
            'phone_number',
            'email',
            'password',
            'is_active',
            'is_admin',
            'is_staff',

        ]
        widgets = {
            'first_name'  : forms.TextInput(attrs={'class': 'form-control','placeholder' : 'Enter Firstname'}),
            'last_name'  : forms.TextInput(attrs={'class': 'form-control','placeholder' : 'Enter Lastname'}),
            'username'  : forms.TextInput(attrs={'class': 'form-control','placeholder' : 'Enter Username'}),
            'phone_number' : forms.TextInput(attrs={'class': 'form-control','placeholder' : 'Enter Mobile Number',}),
            'email'  : forms.EmailInput(attrs={'class': 'form-control','placeholder' : 'Enter Email',"pattern" : '[^@]+@[^@]+\.[a-zA-Z]{2,6} required'}),
            'password'  : forms.PasswordInput(attrs={'class': 'form-control','placeholder' : 'Enter Password'}),
            'is_active' : forms. CheckboxInput(),
            'is_admin' : forms. CheckboxInput(),
            'is_staff' : forms. CheckboxInput(),
        }



class UserProfilePicForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['profile_pic']        
               

class AddressForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        model = Addresses
        exclude = ('user','is_default','is_active')  



class AddressCountryForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        fields = ['country']
        model = Addresses


      
        

        

