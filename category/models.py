
from curses import meta
from distutils.command.upload import upload
from tabnanny import verbose
import uuid
from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True,primary_key=True, editable=False)
    category_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100,unique= True)
    description = models.CharField(max_length=500,blank=True, null=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name ='category'
        verbose_name_plural = 'categories'

    def get_url(self):
       return reverse('products_by_category', args=[self.slug])    

    def __str__(self) -> str:
        return self.category_name

    
