from django.shortcuts import render
from articles.models import Article
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Create your views here.
def blog_list(request):
        list = Article.objects.order_by('position').all()
        return render(request, 'blog/list.html' ,{'list':list})

@require_POST
def sort_articles(request):
    try:
        # 1. Parse the JSON data sent from the template
        data = json.loads(request.body)
        new_order_ids = data.get('order')  # Example: [12, 5, 8, 1]

        # 2. Update the position for each Article based on the new list order
        for index, article_id in enumerate(new_order_ids):
            # We use filter().update() which is faster than getting and saving the object
            Article.objects.filter(id=article_id).update(position=index)

        return JsonResponse({'status': 'success', 'message': 'Order saved!'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)