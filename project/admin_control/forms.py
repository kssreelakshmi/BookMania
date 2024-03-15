from django import forms
from coupon.models import Coupon


class CouponForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'    
        self.fields['expire_date'].widget.attrs['type'] = 'date'    

    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'expire_date': forms.DateInput(attrs={'type': 'date'})
        }