from django.shortcuts import render, redirect
from .models import Blog
from .forms import BlogForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404



@login_required
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
    print("Session data:", dict(request.session))  

    return render(request, 'blog/list.html', {
        'list': blog, 
        'current_filter': current_filter
    })



@login_required
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



@login_required
def edit_blog(request, slug):
    # Retrieve the blog object or return 404 if not found
    blog = get_object_or_404(Blog, slug=slug)

    # Get the session filter
    session_filter = request.session.get('homepage_filter', '0')
    homepage = (session_filter == '1')

    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.homepage = homepage  # Ensure homepage matches session filter
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)

    return render(request, 'blog/form.html', {
        'form': form,
        'homepage': homepage,
        'is_edit': True  
    })
