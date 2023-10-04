from django.db import models
from django.contrib.auth.models import User
import os
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

class Company(models.Model): #제조사
    name = models.CharField(max_length=40, unique=True) #제조사명
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    addr = models.CharField(max_length=200, unique=True) #주소
    number = models.CharField(max_length=20, unique=True) #연락처
    mail = models.CharField(max_length=30, unique=True) #이메일
    business_num = models.CharField(max_length=20, unique=True) #사업자등록번호

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/shop/company/{self.slug}/' #IP주소/shop/company/slug/

    class Meta:
        verbose_name_plural = 'Companies'

class Category(models.Model): #카테고리
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/shop/category/{self.slug}/' #IP주소/shop/category/slug/

    class Meta:
        verbose_name_plural = 'Categories'

class Tag(models.Model): #태그
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/shop/tag/{self.slug}/' #IP주소/shop/tag/slug/

class Item(models.Model): #상품아이템
    name = models.CharField(max_length=40, unique=True) #상품명
    description = MarkdownxField() #간단한설명
    code = models.CharField(max_length=10, unique=True) #상품코드
    image = models.ImageField(upload_to='shop/images/%Y/%m/%d/') #상품이미지
    price = models.IntegerField(null=True) #상품가격

    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    like_users = models.ManyToManyField(User, related_name='like_item', blank=True)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return f'/shop/{self.pk}'

    def get_description_markdown(self):
        return markdown(self.description)

class Comment(models.Model):
    post = models.ForeignKey(Item, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author} : {self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://dummyimage.com/50x50/ced4da/6c757d.jpg'