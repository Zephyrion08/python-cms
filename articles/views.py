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

    # 2. Handle Homepage Filter
    homepage_filter = request.GET.get('homepage', 'no')
    if homepage_filter == 'yes':
        articles_qs = articles_qs.filter(show_on_homepage=True)
    elif homepage_filter == 'no':
        articles_qs = articles_qs.filter(show_on_homepage=False)

    # 3. Handle AJAX Live Search (No new page needed)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('articles/list.html', {'articles': articles_qs}, request=request)
        match = re.search(r'<tbody id="sortable-tbody">([\s\S]*?)</tbody>', html)
        tbody_content = match.group(1) if match else ""
        return JsonResponse({'html': tbody_content})

    # 4. Handle per_page dropdown
    per_page = request.GET.get('per_page', '10')  # default 10
    if per_page == 'all':
        page_obj = articles_qs  # show all articles without pagination
        paginate = False
    else:
        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 10
        paginator = Paginator(articles_qs, per_page)
        page_obj = paginator.get_page(request.GET.get('page'))
        paginate = True

    return render(request, 'articles/list.html', {
        'articles': page_obj,
        'page_obj': page_obj if paginate else None,
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
            else:
                messages.success(request, "Article created successfully!")

            return redirect("article_list")
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


