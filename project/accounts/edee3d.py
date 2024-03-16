from django import forms
from django.core.validators import RegexValidator
from .models import Account

class UserSignupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
        help_text=("Password must be at least 8 characters long and contain a mix of uppercase, lowercase, numbers, and symbols."),
        validators=[RegexValidator(
            regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            message='Password must be strong: uppercase, lowercase, number, and symbol (min. 8 chars)'
        )]
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'email', 'password', 'is_active', 'is_admin', 'is_staff']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Firstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Lastname'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mobile Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'is_active': forms.CheckboxInput(),
            'is_admin': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
        }
