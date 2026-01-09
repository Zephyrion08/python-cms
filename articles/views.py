from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator



@ensure_csrf_cookie
@login_required
def article_list(request):
    articles_qs = Article.objects.all().order_by('-created_at')

    paginator = Paginator(articles_qs, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)

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







    if request.method == "POST":
        # Get the list of selected article IDs
        selected_ids = request.POST.getlist('selected_ids')
        action = request.POST.get('action')

        if not selected_ids:
            messages.warning(request, "No articles selected.")
            return redirect('article_list')

        # Filter only articles the user is allowed to modify
        articles = Article.objects.filter(id__in=selected_ids)

        # Optional: only allow author or superuser
        articles = articles.filter(author=request.user) | articles.filter(author__isnull=False, author__is_superuser=True)
        
        # Perform the chosen action
        if action == "delete":
            for article in articles:
                if article.image:
                    article.image.delete(save=False)  # delete image file
                article.delete()
            messages.success(request, "Selected articles deleted successfully!")

        elif action == "activate":
            articles.update(is_active=True)
            messages.success(request, "Selected articles activated successfully!")

        elif action == "deactivate":
            articles.update(is_active=False)
            messages.success(request, "Selected articles deactivated successfully!")

        else:
            messages.warning(request, "Invalid action.")

    return redirect('article_list')