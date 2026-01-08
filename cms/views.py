from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from articles.models import Article
from django.db.models import FileField
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages


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
def delete_object(request, model_name, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    model_map = {
        "article": Article,
        "user": User,
    }

    model_class = model_map.get(model_name.lower())
    if not model_class:
        messages.error(request, "Invalid model type.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    obj = get_object_or_404(model_class, pk=pk)

    # Permission check for User deletion
    if model_class is User and not request.user.is_superuser:
        messages.error(request, "Only a superuser can delete a user.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Store the title or name before deleting to show in the message
    obj_name = getattr(obj, 'title', getattr(obj, 'username', 'Item'))

    # Your manual file cleanup (though your global signal handles this too!)
    for field in obj._meta.fields:
        if isinstance(field, FileField):
            file = getattr(obj, field.name)
            if file:
                file.delete(save=False)

    obj.delete()
    
    # Success Message
    messages.error(request, f'"{obj_name}" has been deleted successfully.')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')