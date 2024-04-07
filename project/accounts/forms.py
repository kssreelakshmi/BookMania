from django import forms
from accounts.models import Account,Addresses,ContactMessage
from django.contrib.auth.forms import PasswordResetForm
from django.core.validators import RegexValidator,EmailValidator



class UserSignupForm(forms.ModelForm):

    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),help_text=("Password must be at least 8 characters long and contain a mix of uppercase, lowercase, numbers, and symbols."),
        validators=[RegexValidator(regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",message='Password must be strong: uppercase, lowercase, number, and symbol (min. 8 chars)',),])
    

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
            'email'  : forms.EmailInput(attrs={'class': 'form-control','placeholder' : 'Enter Email'}),
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


class ContactUsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
      
    class Meta:
        model = ContactMessage
        fields = '__all__'




