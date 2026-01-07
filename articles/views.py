from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


@login_required
def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'articles/list.html', {'articles': articles})


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

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)

            # Handle image removal
            if request.POST.get('remove_image') == '1' and article.image:
                article.image.delete(save=False)
                article.image = None

            article.save()
            messages.success(request, "Article saved successfully!")
            return redirect('article_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/form.html', {
        'form': form,
        'is_edit': True,
    })




@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Only author or superuser can delete
    if article.author != request.user and not request.user.is_superuser:
        return redirect('article_list')

    if request.method == 'POST':
        # Delete the image file if it exists
        if article.image:
            article.image.delete(save=False)  # <-- removes file from disk
            

        # Delete the article instance
        article.delete()
        messages.error(request, "Article delete successfully!")

    return redirect('article_list')
