from django import forms
from .models import Article
from django.utils.text import slugify

class ArticleForm(forms.ModelForm):
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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if not self.instance.pk:  # hide slug on create
    #         self.fields.pop('slug')

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
