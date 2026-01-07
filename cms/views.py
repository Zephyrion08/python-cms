from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from articles.models import Article

@login_required
def toggle_status(request, model_name, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    # map model_name to actual model
    model_map = {
        "article": Article,

    }

    model_class = model_map.get(model_name.lower())
    if not model_class:
        return JsonResponse({"error": "Invalid model"}, status=400)

    obj = get_object_or_404(model_class, pk=pk)
    obj.is_active = not obj.is_active
    obj.save()
    return JsonResponse({"status": obj.is_active})


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')