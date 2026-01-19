from django.shortcuts import render, redirect
from .models import Blog
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import BlogForm

def blog_list(request):
    # 1. Capture the parameter if it exists in the URL
    homepage_param = request.GET.get('homepage')
    
    if homepage_param is not None:
        # Save the choice to the session
        request.session['homepage_filter'] = homepage_param
        # Redirect to the 'clean' URL (removes ?homepage=X from address bar)
        return redirect('blog_list')

    # 2. Get the value from session, default to '1' (Inner Page) if session is empty
    current_filter = request.session.get('homepage_filter', '0')

    # Filtering
    blog = Blog.objects.filter(homepage=current_filter).order_by('position')

    return render(request, 'blog/list.html', {
        'list': blog, 
        'current_filter': current_filter
    })


def create_blog(request):
    session_filter = request.session.get('homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            # Commit=False lets us modify the object before saving to DB
            blog = form.save(commit=False)
            blog.homepage = homepage 
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm(initial={'homepage': homepage})

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage
    })