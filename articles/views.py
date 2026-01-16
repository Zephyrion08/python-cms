from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
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
    if per_page == 'all':
        per_page = articles_qs.count()  # show everything
    else:
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
    
    context = {
        'articles': page_obj,
        'page_obj': page_obj,
        'per_page': per_page,
    }
    
    # If this is an AJAX request, return only the list partial HTML
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('articles/_list_partial.html', context, request=request)
        return HttpResponse(html)
    
    return render(request, 'articles/list.html', context)


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
            
            # Get the action from the form
            action = request.POST.get('action', 'save_and_quit')
            
            # Handle different actions
            if action == 'save':
                # Stay on edit page
                messages.success(request, "Article created successfully!")
                return redirect('article_edit', slug=article.slug)
            elif action == 'save_and_new':
                # Go back to create form
                messages.success(request, "Article created! Add another one.")
                return redirect(reverse("article_create") + f"?from_homepage={'yes' if force_homepage else 'no'}")
            else:  # save_and_quit
                # Go back to list
                messages.success(request, "Article created successfully!")
                if force_homepage:
                    return redirect(reverse("article_list") + "?homepage=yes")
                else:
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
            # show_on_homepage is preserved automatically since it's not in the form
            updated_article = form.save()
            
            # Get the action from the form
            action = request.POST.get('action', 'save_and_quit')
            
            # Handle different actions
            if action == 'save':
                # Stay on edit page
                messages.success(request, "Article updated successfully!")
                return redirect('article_edit', slug=updated_article.slug)
            elif action == 'save_and_new':
                # Go to create form
                messages.success(request, "Article updated! Create another one.")
                from_homepage = 'yes' if updated_article.show_on_homepage else 'no'
                return redirect(reverse("article_create") + f"?from_homepage={from_homepage}")
            else:  # save_and_quit
                # Go back to list
                messages.success(request, "Article updated successfully!")
                if updated_article.show_on_homepage:
                    return redirect(reverse("article_list") + "?homepage=yes")
                else:
                    return redirect(reverse("article_list") + "?homepage=no")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm(instance=article)
    
    return render(request, "articles/form.html", {
        "form": form,
        "is_edit": True,
        "article": article,
    })