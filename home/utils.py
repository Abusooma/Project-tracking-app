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



# Remplir les models par defaut

contenu_models = {
    'A': [
         "Revue logistique",
          "Création l’arborescence du produit", 
          "Traitement FT315", 
          "Réalisation DFM XT763 ( Livrable)",  
          "Initiation Tryptique (livrable)", 
          "Simogramme", 
          "Initiation analyse capacitaire XT443 (si besoin)", 
          "Organiser les réunions Test /conception produit", 
          "Critical Design Review"
          ],
    'B': [
        "Revue AMDEC et PS", 
        "Définir la liste des outillages", 
        "Récupération des CAO et 3D mécanique",
        "Elaboration les CDC => lancement outillage",
        "Lancement les écrans FT295 + cadre (si besoin)",
	    "Avoir un planning des outillages", 
	    "Suivi Avancement", 
	    "Création Dossier Proto : FT206",  
	    "Organisation Revue Industrielle : FT799",  
	    "Réalisation Proto",
	    "Analyse critique assemblage FT211",
        "Récupération les spécification produit (poids, exigences ..)",
	    "Création une demande étiquette produit",
	    "Valider protype emballage et etiquette", 
	    "Mise à jour de la nomenclature", 
	    "Passage B –Model Review"
],
'C': [
    	"Création Dossier Proto",   
	    "Réalisation Proto  ",
	    "Liste des composants réparable : FT 653-(livrable)",
        "Retour LUP",
	    "Passage CMR",
        "Rapport de qualification outillage : FT790"
],
'Ramp up': [
    	"Finalisation simograme : XT446",   		
	    "Vérification chiffrage MOD / Dossier de fab",		
	    "Analyse capacitaire XT443-(livrable)",		
	    "Réalisation audit Interne", 
	    "Accompagner la production : ajustement et réglage process (si besoin)",   		
	    "Suivi FPY : validation la montée en cadence",   		
	    "MPR Validé"
]


}

noms_models = list(contenu_models.keys())

