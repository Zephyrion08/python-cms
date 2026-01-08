import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField



class Article(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, blank=True) # blank=True so form doesn't require it

    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    content = RichTextUploadingField(blank=True)
    show_on_homepage = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Unique Slug Logic
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

