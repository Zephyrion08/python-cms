from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'subtitle', 'content','homepage','active']
        widgets = {
            # This keeps the field in the form but hides it from the user's eyes
            'homepage': forms.HiddenInput(),
        }
