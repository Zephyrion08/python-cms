from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse



@ensure_csrf_cookie
@login_required
def article_list(request):
    articles_qs = Article.objects.all().order_by('position')
    
    # 1. Handle Search
    query = request.GET.get('q', '')
    if query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=query) | Q(slug__icontains=query)
        )

    # 2. Handle AJAX Live Search (No new page needed)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # We render the SAME template but only a specific block or just loop the rows
        html = render_to_string('articles/list.html', {'articles': articles_qs}, request=request)
        # We use a trick: extract only the <tbody> content from the rendered string
        import re
        tbody_content = re.search(r'<tbody id="sortable-tbody">([\s\S]*?)</tbody>', html).group(1)
        return JsonResponse({'html': tbody_content})

    # 3. Standard Pagination for initial load
    paginator = Paginator(articles_qs, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'articles/list.html', {
        'articles': page_obj,
        'page_obj': page_obj,
    })

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user

            # Delete image if remove_image is 1
            if request.POST.get('remove_image') == '1' and article.image:
                article.image.delete(save=False)
                article.image = None

            article.save()
            messages.success(request, "Article saved successfully!")
            return redirect('article_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm()

    return render(request, 'articles/form.html', {'form': form})


@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # 1. Security: Only author or superuser can edit
    if article.author != request.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to edit this article.")
        return redirect('article_list')

    if request.method == 'POST':
        # 2. Check the custom 'remove_image' flag from your JS
        remove_image_flag = request.POST.get('remove_image') == '1'
        
        form = ArticleForm(request.POST, request.FILES, instance=article)
        
        if form.is_valid():
            article = form.save(commit=False)
            
            # 3. If user clicked 'X' and didn't upload a new one, clear the field
            # The signal in models.py will handle the actual file deletion
            if remove_image_flag and not request.FILES.get('image'):
                article.image = None
                
            article.save()
            messages.success(request, "Article updated successfully!")
            return redirect('article_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/form.html', {
        'form': form,
        'is_edit': True,
        'article': article, 
    })


