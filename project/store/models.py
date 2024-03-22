from django.db import models
from category.models import Category
from accounts.models import Account
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Avg,Count


#  Create your models here.
def validate_file_type(file):
   
    allowed_mimetypes = ['image/jpeg', 'image/png']  
    mime_type = file.content_type
    if mime_type not in allowed_mimetypes:
        raise ValidationError("Invalid file type. Only JPEG and PNG images are allowed.")

class Attribute(models.Model):
    attribute_name = models.CharField(max_length=150,unique=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.attribute_name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete=models.CASCADE)
    attribute_value = models.CharField(max_length=250,unique=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return str(self.attribute) + "-" + self.attribute_value

class Publication(models.Model):
    name = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name
    
class Author(models.Model):
    author_name = models.CharField(max_length=50,unique=True)
    is_active = models.BooleanField(default=True)
    author_created_at = models.DateTimeField(auto_now_add=True)
    author_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author_name


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255,blank = True, unique=True)
    description = models.TextField(max_length=500,blank=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        product_slug_name = f'{self.publication.name}-{self.product_name}-{self.category.category_name}'
        base_slug = slugify(product_slug_name)
        counter = Product.objects.filter(slug__startswith=base_slug).count()
        if counter > 0:
            self.slug = f'{base_slug}-{counter}'
        else:
            self.slug = base_slug
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.product_name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    attribute = models.ManyToManyField(AttributeValue,related_name='attributes')
    sku_id = models.IntegerField()
    max_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField()
    product_variant_slug = models.SlugField(max_length=255,unique=True)
    thumbnail_image = models.ImageField(upload_to='photos/product-variant/thumbnail', validators=[validate_file_type])
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        product_variant_slug_name = f'{self.product.publication.name}-{self.product.product_name}-{self.product.category.category_name}-{self.sku_id}'
        base_slug = slugify(product_variant_slug_name)
        counter = ProductVariant.objects.filter(product_variant_slug__startswith=base_slug).count()
        if counter > 0:
            self.product_variant_slug = f'{base_slug}-{counter}'
        else:
            self.product_variant_slug = base_slug
        super(ProductVariant, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('product_variant_detail',args=[self.product.category.slug,self.product_variant_slug])
    
    def get_product_name(self):
        return f'{self.product.product_name}-{self.sku_id} - {", ".join([value[0] for value in self.attribute.all().values_list("attribute_value")])} by {self.product.publication}'
    
    def average_review(self):
        from store.models import ReviewRating    
        reviews = ReviewRating.objects.filter(product_variant=self,status=True).aggregate(average=Avg('rating'))
        print(reviews)
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def count_review(self):
        from store.models import ReviewRating    
        reviews = ReviewRating.objects.filter(product_variant=self,status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def __str__(self):
        return self.product_variant_slug



class AdditionalProductImages(models.Model):
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name='additional_product_images')
    image = models.ImageField(upload_to='photos/product-variant/additional-images',validators=[validate_file_type])
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.image.url
    

class ReviewRating(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE, related_name='product_review')
    subject = models.CharField(max_length =200,blank = True)
    review = models.TextField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=50,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject  

class RecentViewedProduct(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Get the total count of rows in the table
        total_rows = RecentViewedProduct.objects.filter(user=self.user).count()

        if total_rows >= 7:
            oldest_row = RecentViewedProduct.objects.filter(user=self.user).order_by('updated_at').first()
            oldest_row.delete()

        super(RecentViewedProduct, self).save(*args, **kwargs)
        

    def __str__(self):
        return self.user.first_name+" "+self.product.get_product_name()




 


    

    

