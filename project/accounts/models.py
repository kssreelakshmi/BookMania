from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils import timezone
from django_countries.fields import CountryField
from django.core.validators import RegexValidator,EmailValidator
import datetime
import uuid
# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password,phone_number):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            phone_number = phone_number
        )

        user.set_password(password)
        user.save(using= self._db)
        return user
    
    def create_superuser(self,first_name,last_name,email,username,password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,

        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_verified = True
        user.save(using = self._db)
        return user

class Account(AbstractBaseUser):
    pattern=r"^[6-9]\d{9}$"
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True,validators = [EmailValidator()])
    phone_number = models.CharField(max_length=15, validators = [RegexValidator(pattern)] )
    profile_pic = models.ImageField(upload_to='photos/user-profile/user-images',null=True,blank=True)

    #required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','phone_number', 'first_name','last_name']

    objects = AccountManager()


    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete = models.CASCADE, related_name = 'user_profile')
    otp = models.CharField(max_length = 6)
    uid = models.UUIDField(default = uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add = True)

    @property
    def delete_after_five_minutes(self):
        time = self.created_at + datetime.timedelta(seconds=5)
        if time > datetime.datetime.now():
            e = UserProfile.objects.get(pk=self.pk)
            e.delete()
            return True
        else:
            return False
             
    def __str__(self):
        return self.otp

class Addresses(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50,blank=True,null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = CountryField()
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)    
    
    def save(self, *args, **kwargs):
        if self.is_default:
    
            Addresses.objects.filter(user = self.user).exclude(pk=self.pk).update(is_default=False)
        super(Addresses, self).save(*args, **kwargs)
        
    def get_user_full_address(self):
        address_parts = f"{self.name}, {self.phone_number}, {self.address_line_1}"
        
        if self.address_line_2:
            address_parts += (', '+self.address_line_2)
        
        address_parts += (f", Pin: {self.pincode}, {self.city}, {self.state}, {self.country.name}")
        
        
        return address_parts
        # return f'{self.name},{self.phone},Pin:{self.pincode},Address:{self.address_line_1},{self.address_line_2},{self.city},{self.state},{self.country}'
    
    def __str__(self):
        return self.name






class ContactMessage(models.Model):
    user = models.ForeignKey(Account,max_length=100, on_delete = models.CASCADE)
    email = models.EmailField()
    subject = models.CharField(max_length=128)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user    
                                                                                                                                                                              
    
    
    
  