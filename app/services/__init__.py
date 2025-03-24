from django.shortcuts import get_object_or_404
from django.db.models import Q
from app.utils import *
from asgiref.sync import *

async def update_model_object(model_obj, update_dict):
    for key, value in update_dict.items():
        setattr(model_obj, key, value)
    model_obj.asave()

@sync_to_async
def filter_objects_sync(model_class, filters):
    return list(
        model_class.objects.filter(**filters).values()
        )