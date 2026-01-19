import json
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Case, When, Value, BooleanField
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib import messages
from django_ratelimit.decorators import ratelimit

from articles.models import Article
from blog.models import Blog

User = get_user_model()
logger = logging.getLogger(__name__)

# -------------------------
# Global Constants / Helpers
# -------------------------
MODEL_MAP = {
    "article": Article,
    "user": User,
    "blog": Blog,
}

def redirect_back(request, default='/'):
    """Redirect to previous page or default"""
    return redirect(request.META.get('HTTP_REFERER', default))

def get_obj_name(obj):
    """Return a display name for object"""
    return getattr(obj, 'title', getattr(obj, 'username', str(obj)))

def check_user_permission(request, model_class, action="change"):
    """
    Simple permission check:
    - Superuser: Can do anything
    - User model: Superuser only
    - Article model: All logged-in users
    """
    # Superuser can do anything
    if request.user.is_superuser:
        return True
    
    # User model operations - superuser only
    if model_class is User:
        return False
    
    # Article model - all logged-in users can manage
    if model_class is Article:
        return True
    
    # Default: deny
    return False

# -------------------------
# Views
# -------------------------
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@ratelimit(key='user', rate='30/m', method='POST')
@login_required
@require_POST
def toggle_status(request, model_name, pk):
    """Toggle is_active status of an object"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({"error": "Invalid model"}, status=400)

    obj = get_object_or_404(model_class, pk=pk)

    if not check_user_permission(request, model_class, action="change"):
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Toggle is_active safely
    obj.is_active = not obj.is_active
    obj.save(update_fields=['is_active'])

    return JsonResponse({
        "status": obj.is_active,
        "message": f'"{get_obj_name(obj)}" status changed.'
    })


@ratelimit(key='user', rate='30/m', method='POST')
@login_required
@require_POST
def delete_object(request, model_name, pk):
    """Delete a single object"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        messages.error(request, "Invalid model type.")
        return redirect_back(request)

    obj = get_object_or_404(model_class, pk=pk)

    if not check_user_permission(request, model_class, action="delete"):
        messages.error(request, "You do not have permission to delete this item.")
        return redirect_back(request)

    obj_name = get_obj_name(obj)
    obj.delete()

    messages.success(request, f'"{obj_name}" has been deleted successfully.')
    return redirect_back(request)


@ratelimit(key='user', rate='30/m', method='POST')
@login_required
@require_POST
def bulk_action(request, model_name):
    """Perform bulk actions (toggle status or delete)"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        messages.error(request, "Invalid model type.")
        return redirect_back(request)

    # Check permission
    if not check_user_permission(request, model_class, action="change"):
        messages.error(request, "You do not have permission for this action.")
        return redirect_back(request)

    selected_ids = request.POST.getlist("selected_ids") or request.POST.get("ids", "").split(',')
    selected_ids = [id_val for id_val in selected_ids if id_val]

    if not selected_ids:
        messages.warning(request, "No items selected.")
        return redirect_back(request)

    action = request.POST.get("action") or ("delete" if request.POST.get("ids") else None)
    queryset = model_class.objects.filter(pk__in=selected_ids)

    if action == "toggle":
        queryset.update(
            is_active=Case(
                When(is_active=True, then=Value(False)),
                When(is_active=False, then=Value(True)),
                output_field=BooleanField()
            )
        )
        messages.success(request, f"{queryset.count()} {model_name}(s) status toggled.")

    elif action == "delete":
        count = queryset.count()
        queryset.delete()
        messages.success(request, f"{count} {model_name}(s) deleted successfully.")

    else:
        messages.error(request, "Invalid action.")

    return redirect_back(request)


@ratelimit(key='user', rate='60/m', method='POST')
@login_required
@require_POST
def update_order(request, model_name):
    """Update position order for drag-and-drop"""
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({'status': 'error', 'message': 'Invalid model type'}, status=400)

    # Check permission
    if not check_user_permission(request, model_class, action="change"):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        order = data.get('order', [])

        # Validate and convert IDs to integers
        try:
            order = [int(obj_id) for obj_id in order]
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid ID format'}, status=400)

        # Get objects and create mapping
        objs = model_class.objects.filter(id__in=order)
        obj_map = {obj.id: obj for obj in objs}

        # Update positions
        updated_objs = []
        for position, obj_id in enumerate(order):
            if obj_id in obj_map:
                obj = obj_map[obj_id]
                obj.position = position
                updated_objs.append(obj)

        # Bulk update in transaction
        with transaction.atomic():
            model_class.objects.bulk_update(updated_objs, ['position'])

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        logger.error("Invalid JSON in update_order")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to update order'}, status=500)
    

    
@ratelimit(key='user', rate='30/m', method='GET')
@login_required
def ajax_check_slug(request, model_name):
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({
            "error": "Invalid model",
            "slug": "",
            "exists": False
        }, status=400)
    
    # Check if model has slug field
    if not hasattr(model_class, 'slug'):
        return JsonResponse({
            "error": f"{model_name} does not have a slug field",
            "slug": "",
            "exists": False
        }, status=400)
    
    # Get slug directly from request (not title)
    slug = request.GET.get("slug", "").strip()
    object_id = request.GET.get("object_id", "").strip()
    
    # Validate inputs
    if not slug:
        return JsonResponse({
            "error": "Slug is required",
            "slug": "",
            "exists": False
        }, status=400)
    
    # Slugify the input to ensure it's valid
    from django.utils.text import slugify
    slug = slugify(slug)
    
    if not slug:
        return JsonResponse({
            "error": "Invalid slug format",
            "slug": "",
            "exists": False
        }, status=400)
    
    # Check if slug exists in database
    qs = model_class.objects.filter(slug=slug)
    
    # Exclude current object if editing
    if object_id and object_id.isdigit():
        qs = qs.exclude(pk=int(object_id))
    
    return JsonResponse({
        "slug": slug,
        "exists": qs.exists()
    })