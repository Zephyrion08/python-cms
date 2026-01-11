from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Case, When, Value, BooleanField
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib import messages
import json

from articles.models import Article

User = get_user_model()

# -------------------------
# Global Constants / Helpers
# -------------------------
MODEL_MAP = {
    "article": Article,
    "user": User,
}

def redirect_back(request, default='/'):
    return redirect(request.META.get('HTTP_REFERER', default))

def get_obj_name(obj):
    """Return a display name for object"""
    return getattr(obj, 'title', getattr(obj, 'username', str(obj)))

def check_user_permission(request, model_class, action="change"):
    """Simple permission check helper"""
    if model_class is Article and action == "change" and not request.user.has_perm('articles.change_article'):
        return False
    if model_class is User and not request.user.is_superuser:
        return False
    return True

# -------------------------
# Views
# -------------------------
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
@require_POST
def toggle_status(request, model_name, pk):
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({"error": "Invalid model"}, status=400)

    obj = get_object_or_404(model_class, pk=pk)

    if not check_user_permission(request, model_class, action="change"):
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Toggle is_active safely across all DBs
    obj.is_active = not obj.is_active
    obj.save(update_fields=['is_active'])

    return JsonResponse({
        "status": obj.is_active,
        "message": f'"{get_obj_name(obj)}" status changed.'
    })


@login_required
@require_POST
def delete_object(request, model_name, pk):
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


@login_required
@require_POST
def bulk_action(request, model_name):
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        messages.error(request, "Invalid model type.")
        return redirect_back(request)

    selected_ids = request.POST.getlist("selected_ids") or request.POST.get("ids", "").split(',')
    selected_ids = [id_val for id_val in selected_ids if id_val]  # remove empty strings

    if not selected_ids:
        messages.warning(request, "No items selected.")
        return redirect_back(request)

    action = request.POST.get("action") or ("delete" if request.POST.get("ids") else None)
    queryset = model_class.objects.filter(pk__in=selected_ids)

    if action == "toggle":
        # Ensure safe toggle across DBs
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


@login_required
@require_POST
def update_order(request, model_name):
    model_class = MODEL_MAP.get(model_name.lower())
    if not model_class:
        return JsonResponse({'status': 'error', 'message': 'Invalid model type'}, status=400)

    try:
        data = json.loads(request.body)
        order = data.get('order', [])
        order = data.get('order', [])

        # Force IDs to integers
        try:
            order = [int(obj_id) for obj_id in order]
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid ID format'}, status=400)

        objs = model_class.objects.filter(id__in=order)
        obj_map = {obj.id: obj for obj in objs}

        updated_objs = []
        for position, obj_id in enumerate(order):
            if obj_id in obj_map:
                obj = obj_map[obj_id]
                obj.position = position
                updated_objs.append(obj)

        with transaction.atomic():
            model_class.objects.bulk_update(updated_objs, ['position'])

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
