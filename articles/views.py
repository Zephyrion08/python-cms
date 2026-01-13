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
import re
from django.urls import reverse

@ensure_csrf_cookie
@login_required
def article_list(request):
    articles_qs = Article.objects.select_related('author').order_by('position')

    # Search
    query = request.GET.get('q', '')
    
    if query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=query) | Q(slug__icontains=query)
        )

    # Homepage filter
    homepage_filter = request.GET.get('homepage', 'no')
    if homepage_filter == 'yes':
        articles_qs = articles_qs.filter(show_on_homepage=True)
    else:
        articles_qs = articles_qs.filter(show_on_homepage=False)

    # Per page
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page < 1:
            per_page = 10
        elif per_page > 100:
            per_page = 100
    except ValueError:
        per_page = 10

    # Paginate results
    paginator = Paginator(articles_qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Remove AJAX handling - always return full page with pagination
    return render(request, 'articles/list.html', {
        'articles': page_obj,
        'page_obj': page_obj,
        'per_page': per_page,
    })




@login_required
def article_create(request):
    # Detect if the article should be forced to show on homepage
    force_homepage = request.GET.get('from_homepage') == 'yes'

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.show_on_homepage = force_homepage
            article.save()

            if force_homepage:
                messages.success(request, "Article added to Homepage!")
                return redirect(reverse("article_list") + "?homepage=yes")
            else:
                messages.success(request, "Article created successfully!")
                return redirect(reverse("article_list") + "?homepage=no")

        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm()

    return render(request, "articles/form.html", {
        "form": form,
        "is_edit": False,
        "force_homepage": force_homepage,
    })

@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article updated successfully!")
            return redirect("article_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/form.html", {
        "form": form,
        "is_edit": True,
        "article": article,
    })