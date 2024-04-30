from django.db import models
from django.contrib import admin
from core import settings


class Chef_de_Projet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    Chef_de_Projet_name = models.CharField(max_length=200, null=True)
    Chef_de_Projet_Prenom = models.CharField(max_length=200)
    Chef_de_Projet_mail = models.CharField(max_length=200)
    Chef_de_Projet_mot_de_passe = models.CharField(max_length=200)

    idChef_de_Projet = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Chef_de_Projet_name


class Responsable_Projet(admin.ModelAdmin):
    list_display = ('Chef_de_Projet_name', 'Chef_de_Projet_Prenom',)
    search_fields = ['Chef_de_Projet_name', 'Chef_de_Projet_Prenom', ]


##


class Equipe_de_Projet(models.Model):
    Nom_Employe = models.CharField(max_length=200, null=True)
    Services = models.CharField(max_length=200)

    idProjet = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Nom_Employe


class Teams_Projet(admin.ModelAdmin):
    list_display = ('Nom_Employe', 'Services',)
    search_fields = ['Nom_Employe', 'Services', ]


##


class Categorie(models.Model):
    Domaine_dactivite = models.CharField(max_length=200, null=True)

    iddomaine_dactivite = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Domaine_dactivite


class genre(admin.ModelAdmin):
    list_display = ('Domaine_dactivite',)
    search_fields = ['Domaine_dactivite', ]


##


class Livrable(models.Model):
    nom_livrable = models.CharField(max_length=200, null=True)
    Ref_livrable = models.CharField(max_length=200, null=True)
    Type = models.CharField(max_length=200, null=True)

    idlivrable = models.AutoField(primary_key=True)

    def __str__(self):
        return self.nom_livrable


class document(admin.ModelAdmin):
    list_display = ('nom_livrable', 'Ref_livrable', 'Type')
    search_fields = ['Type', ]


##


class Cycle_de_devellopement(models.Model):
    type = models.CharField(max_length=200, null=True)
    Date_debut = models.CharField(max_length=200)
    Date_Fin = models.CharField(max_length=200)
    Priorite = models.CharField(max_length=200)

    # clé étrangère d'une autre table #
    nom_livrable = models.ForeignKey(Livrable, on_delete=models.CASCADE, null=True)
    ##
    idphase = models.AutoField(primary_key=True)

    def __str__(self):
        return self.type


class Cycle_de_vie(admin.ModelAdmin):
    list_display = ('type', 'Priorite',)
    search_fields = ['type', 'Priorite', ]


##

class Etape(models.Model):
    # clé étrangère d'une autre table #
    type = models.ForeignKey(Cycle_de_devellopement, on_delete=models.CASCADE, null=True)
    #
    num_etape = models.CharField(max_length=200, null=True)
    nom_etape = models.CharField(max_length=200, null=True)
    Statut = models.CharField(max_length=200, null=True)
    Commentaire = models.CharField(max_length=200, null=True)

    idEtape = models.AutoField(primary_key=True)

    def __str__(self):
        return self.nom_etape


class sequence(admin.ModelAdmin):
    list_display = ('type', 'num_etape', 'nom_etape', 'Statut', 'Commentaire',)
    search_fields = ['Statut', ]


##


class Client(models.Model):
    Nom_Client = models.CharField(max_length=200, null=True)
    Adresse = models.CharField(max_length=200)
    # clé étrangère d'une autre table #
    Domaine_dactivite = models.ForeignKey(Categorie, on_delete=models.CASCADE, null=True)
    ##
    idClient = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Nom_Client


class customer(admin.ModelAdmin):
    list_display = ('Nom_Client', 'Adresse', 'Domaine_dactivite')
    search_fields = ['Nom_Client', 'Adresse', 'Domaine_dactivite']
    list_filter = ['Domaine_dactivite']


class Famille_de_Projet(models.Model):
    Nom_Famille = models.CharField(max_length=200, null=True)

    idFamille = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Nom_Famille


class Family(admin.ModelAdmin):
    list_display = ('Nom_Famille',)
    search_fields = ['Nom_Famille', ]


# CLASS DE "TYPE DE PROCESS" ASSOCIE A UN PROJET
class Process(models.Model):
    nom = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.nom


class ProcessAdmin(admin.ModelAdmin):
    list_display = ('nom',)


class Projet(models.Model):
    nom = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=200)
    nom_client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    chef_de_projet = models.ForeignKey(Chef_de_Projet, on_delete=models.CASCADE, null=True)
    Date_debut = models.DateTimeField(null=True)
    Date_fin = models.DateTimeField(null=True)
    famille_projet = models.ForeignKey(Famille_de_Projet, on_delete=models.CASCADE, null=True)
    type_process = models.ForeignKey(Process, on_delete=models.CASCADE, null=True)
    id_projet = models.AutoField(primary_key=True)

    def __str__(self):
        return self.nom

    def progress(self):
        all_tasks = Tache.objects.filter(projet=self)
        total_progress = sum(task.progression_tache() for task in all_tasks)
        total_tasks_count = all_tasks.count()

        if total_tasks_count == 0:
            return 0.0

        return total_progress / total_tasks_count


# CLASS DE "MODEL" DU "TYPE DE PROCESS" ASSOCIE A UN PROJET
class ModelProcess(models.Model):
    nom = models.CharField(max_length=150)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='models')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nom

    def progression_taches(self):
        """ Calcul la progression des tâches dans un model spécifique d'un type de process """
        total_model_taches = self.tache_set.all().count()
        total_model_taches_achevees = self.tache_set.filter(acheve=True).count()
        if total_model_taches == 0:
            return 0.0
        return (total_model_taches_achevees / total_model_taches) * 100


class ModelProcessAdmin(admin.ModelAdmin):
    list_display = ('nom', 'process',)
    search_fields = ['nom', 'process']
    list_filter = ['nom']


# CLASS DE TACHES D'UN MODEL SPECIFIQUE D'UN PROCESS ASSOCIE A UN PROJET DONNE
class Tache(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(ModelProcess, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    date_achevement = models.DateTimeField(null=True, blank=True)
    acheve = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.description} - {'Achevée' if self.acheve else 'Non achevée'}"

    def progression_tache(self):
        return 100 if self.acheve else 0


class TacheAdmin(admin.ModelAdmin):
    list_display = ('model', 'description', 'acheve')


class programme(admin.ModelAdmin):
    list_display = ('nom', 'type_process', 'description', 'nom_client', 'chef_de_projet', 'famille_projet')
    search_fields = ['nom', 'etat', 'description']
    list_filter = ['nom']


##


class Site(models.Model):
    Nom_Site = models.CharField(max_length=200, null=True)
    idsite = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Nom_Site


class emplacement(admin.ModelAdmin):
    list_display = ('Nom_Site',)
    search_fields = ['Nom_Site', ]


##

class Avancement(models.Model):
    etat_avancement = models.CharField(max_length=200, null=True)

    idavancement = models.AutoField(primary_key=True)

    def __str__(self):
        return self.etat_avancement


class Progression(admin.ModelAdmin):
    list_display = ('etat_avancement',)
    search_fields = ['etat_avancement', ]


##

class Equipements(models.Model):
    Nom_Equipement = models.CharField(max_length=200, null=True)
    type_Equipement = models.CharField(max_length=200)
    statut_Equipement = models.CharField(max_length=200)
    Numero_Equipement = models.CharField(max_length=200, null=True)

    idequipement = models.AutoField(primary_key=True)

    def __str__(self):
        return self.Nom_Equipement


class outillage(admin.ModelAdmin):
    list_display = ('Numero_Equipement', 'type_Equipement')
    search_fields = ['statut_Equipement', ]
