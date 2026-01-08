from django import forms
from .models import Article
from django.utils.text import slugify
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ArticleForm(forms.ModelForm):
    # 1. Add the hidden field that your JS targets
    remove_image = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    content = forms.CharField(widget=CKEditorUploadingWidget(),required=False)

    slug = forms.CharField(
        required=False,
        help_text="Auto-generated from title",
        widget=forms.TextInput(attrs={"readonly": "readonly"})
    )

    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'slug', 'image', 'content',
            'show_on_homepage', 'is_active'
        ] 
        widgets = {
            'image': forms.FileInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        slug = slugify(title) if title else ''

        qs = Article.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "An article with this title already exists. Please change the title."
            )

        cleaned_data['slug'] = slug
        return cleaned_data

    # 2. Add the Save logic to handle image removal
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # If the 'X' was clicked in JS, this value will be '1'
        if self.cleaned_data.get('remove_image') == '1':
            instance.image = None # This triggers your global pre_save signal!
            
        if commit:
            instance.save()
        return instance