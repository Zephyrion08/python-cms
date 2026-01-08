from django.contrib import admin
from django.utils.html import format_html
from .models import Article
from django.utils.safestring import mark_safe

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Fields to show in the list view
    list_display = (
        'title',
        'slug',
        'show_on_homepage_icon',
        'is_active_icon',
        'image_thumb',
        'created_at',
        'updated_at'
    )
    
    # Make fields clickable
    list_display_links = ('title', 'slug')
    
    # Filters on the right sidebar
    list_filter = ('show_on_homepage', 'is_active', 'created_at')
    
    # Searchable fields
    search_fields = ('title', 'subtitle', 'content')
    
    # Auto-generate slug from title
    prepopulated_fields = {"slug": ("title",)}
    
    # Readonly fields in admin form
    readonly_fields = ('image_thumb',)
    
    # Function to show image thumbnail
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="object-fit: cover;"/>', obj.image.url)
        return "-"
    image_thumb.short_description = "Image"
    
    # Show homepage flag as icon
    def show_on_homepage_icon(self, obj):
        if obj.show_on_homepage:
            return mark_safe('<span style="color: green;">✔</span>')
        return mark_safe('<span style="color: red;">✖</span>')

    def is_active_icon(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: green;">✔</span>')
        return mark_safe('<span style="color: red;">✖</span>')
