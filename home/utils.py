import random
import string

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Tache


def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def add_permissions_to_group(group_name):
    # Vérifiez d'abord si le groupe existe
    group, _ = Group.objects.get_or_create(name=group_name)
    # Obtenez les autorisations pour le modèle 'Tache'
    content_type = ContentType.objects.get_for_model(Tache)
    permissions = Permission.objects.filter(content_type=content_type)

    # Ajoutez les autorisations au groupe 'chef de projet' s'il n'en a pas déjà
    for permission in permissions:
        if permission not in group.permissions.all():
            group.permissions.add(permission)

