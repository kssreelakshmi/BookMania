from django import forms
from category import models
from .models import Category

category = models.Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name',
            'parent_cat',
            'is_active',
            ]
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_cat': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }