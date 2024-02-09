from django.db import models
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=300, blank=True)
    parent_cat = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE)
    is_active = models.BooleanField(default = True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category,self).save(*args, **kwargs)

    def get_url(self):
        return reverse('products_by_category',args=[self.slug])
    

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    
    def __str__(self):
        return self.category_name
