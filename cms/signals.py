import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db.models import FileField

# 1. Cleanup when object is DELETED
@receiver(post_delete)
def global_delete_files_on_delete(sender, instance, **kwargs):
    """Loop through all fields; if it's a file, delete it from disk."""
    for field in instance._meta.fields:
        if isinstance(field, FileField):
            file = getattr(instance, field.name)
            if file and os.path.isfile(file.path):
                file.delete(save=False)

# 2. Cleanup when file is UPDATED
@receiver(pre_save)
def global_delete_old_files_on_change(sender, instance, **kwargs):
    """Delete the old file when a new one is uploaded."""
    if not instance.pk:
        return False

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    for field in instance._meta.fields:
        if isinstance(field, FileField):
            old_file = getattr(old_instance, field.name)
            new_file = getattr(instance, field.name)
            
            # If the file path has changed, delete the old file
            if old_file and old_file != new_file:
                if os.path.isfile(old_file.path):
                    old_file.delete(save=False)