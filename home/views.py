from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.core.paginator import Paginator
from .utils import generate_random_password, add_permissions_to_group, contenu_models, noms_models


# Vue pour la page d'accueil
def index(request):
    """
    Vue pour la page d'accueil.
    """
    return render(request, 'pages/index.html')


# Vue pour afficher la liste des clients
def clientView(request):
    """
    Vue pour afficher la liste des clients.
    """
    # Récupère tous les clients de la base de données
    all_clients = Client.objects.all()
    # Définit le nombre de clients à afficher par page
    clients_per_page = 5
    # Crée une instance de Paginator pour paginer les clients
    paginator = Paginator(all_clients, clients_per_page)
    # Récupère le numéro de page à afficher
    page_number = request.GET.get('page', 1)
    # Récupère les clients pour la page spécifiée
    clients = paginator.get_page(page_number)

    # Rend la page clients.html avec les clients récupérés
    return render(request, 'pages/clients.html', context={'clients': clients})


# Vue pour créer un nouveau client
def create_client(request):
    """
    Vue pour créer un nouveau client.
    """
    if request.method == 'POST':
        # Crée un formulaire de client avec les données du formulaire POST
        form = ClientForm(request.POST)
        if form.is_valid():
            # Enregistre le client si le formulaire est valide
            form.save()
            # Affiche un message de succès
            messages.success(request, 'Client ajouté avec succès!')
            # Redirige vers la liste des clients
            return redirect('clients')
    else:
        # Crée un nouveau formulaire de client
        form = ClientForm()

        # Rend la page add_client.html avec le formulaire de client
    return render(request, 'pages/add_client.html', {'form': form})


# Vue pour mettre à jour un client existant
def update_client(request, pk):
    """
    Vue pour mettre à jour un client existant.
    """
    # Récupère le client avec l'ID spécifié ou renvoie une erreur 404
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        # Crée un formulaire de client pré-rempli avec les données du client existant
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            # Enregistre les modifications du client si le formulaire est valide
            form.save()
            # Affiche un message de succès
            messages.success(request, 'Client modifié avec succès!')
            # Redirige vers la liste des clients
            return redirect('clients')
        else:
            # Affiche un message d'erreur si le formulaire n'est pas valide
            messages.error(request, 'Quelque chose s\'est mal passé')
    else:
        # Crée un formulaire de client pré-rempli avec les données du client existant
        form = ClientForm(instance=client)

        # Rend la page update_client.html avec le formulaire de client
    return render(request, 'pages/update_client.html', context={'form': form})


# Vue pour supprimer un client
def deleteClient(request, pk):
    """
    Vue pour supprimer un client.
    """
    # Récupère le client avec l'ID spécifié ou renvoie une erreur 404
    client = get_object_or_404(Client, pk=pk)
    # Supprime le client de la base de données
    client.delete()
    # Affiche un message de succès
    messages.success(request, 'Client supprimé avec succès!')
    # Redirige vers la liste des clients
    return redirect('clients')


# ------------------------------Fin::::: Vues de gestion de client -----------------------------


# --------------------------Debut :::::: Vues de gestion de projet------------------------------

@login_required
def display_all_project(request):
    """Vue pour afficher tous les projets"""

    # Récupère le terme de recherche de la requête GET
    query = request.GET.get('query', '')
    # Filtrage des projets basé sur le terme de recherche
    all_projects = Projet.objects.filter(
        Q(nom__icontains=query) | Q(description__icontains=query)
    )

    # Vérifie si l'utilisateur est un chef de projet
    is_chef_projet = hasattr(request.user, 'chef_de_projet')
    if is_chef_projet:
        # Filtrage des projets pour l'utilisateur chef de projet
        all_projects = all_projects.filter(
            chef_de_projet=request.user.chef_de_projet)

    # Nombre de projets à afficher par page
    projects_per_page = 7
    # Crée une instance de Paginator pour paginer les projets
    paginator = Paginator(all_projects, projects_per_page)
    # Récupère le numéro de page à afficher
    page_number = request.GET.get('page', 1)
    # Récupère les projets pour la page spécifiée
    projects = paginator.get_page(page_number)
    context = {
        'projects': projects,
        'query': query,
        'all_projects': all_projects,
        'is_chef_projet': is_chef_projet
    }

    # Rend la page dashboard_display.html avec les projets récupérés
    return render(request, 'admin/dashboard_display.html', context=context)


@login_required
def createProject(request):
    """ Vue pour créer un nouveau projet."""
    if request.method == 'POST':
        # Crée un formulaire de projet avec les données du formulaire POST
        form = ProjetForm(request.POST)
        if form.is_valid():
            # Enregistre le projet si le formulaire est valide
            projet = form.save(commit=False)
            form.save()
            chef_de_projet = projet.chef_de_projet
            # Envoie d'email au chef de projet
            subject = 'Nouveau projet assigné'
            html_content = render_to_string('email/projet_assigne.html',
                                            {'chef_de_projet': chef_de_projet, 'projet': projet})
            email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [
                                           chef_de_projet.Chef_de_Projet_mail])
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=True)

            # Parcours le nom du type de process puis crée le model
            for model_name in projet.type_process.nom.split(', '):
                model = ModelProcess.objects.create(
                    nom=model_name.strip(),
                    process=projet.type_process,
                    projet=projet
                )
                try:
                    model_contenus = contenu_models[model.nom]
                    for model_contenu in model_contenus:
                        tache = Tache(
                            projet=projet,
                            model=model,
                            description=model_contenu,
                            date_achevement=datetime.now(),
                        )
                        tache.save()
                except Exception:
                    print("erreur de creation de tache")

            messages.success(request, 'Projet créé avec succès..!')
            return redirect('display')
    else:
        form = ProjetForm()

    # Rend la page creer_project.html avec le formulaire de projet
    return render(request, 'pages/creer_project.html', {'form': form})


# Vue pour afficher les détails d'un projet
@login_required
def detailProject(request, pk):
    """
    Vue pour afficher les détails d'un projet.
    """
    # Récupère le projet avec l'ID spécifié ou renvoie une erreur 404
    project = get_object_or_404(Projet, pk=pk)
    # Récupère les modèles de processus associés au projet
    modeles = ModelProcess.objects.filter(projet=project)
    # Rend la page detail_project.html avec les détails du projet et ses modèles de processus
    return render(request, 'pages/detail_project.html', context={'projet': project, 'modeles': modeles})


# Vue pour mettre à jour un projet existant
@login_required
def updateProject(request, pk):
    """
    Vue pour mettre à jour un projet existant.
    """
    # Récupère le projet avec l'ID spécifié ou renvoie une erreur 404
    projet = get_object_or_404(Projet, pk=pk)
    old_process = projet.type_process
    if request.method == 'POST':
        # Crée un formulaire de projet pré-rempli avec les données du projet existant
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            project = form.save(commit=False)
            new_process = project.type_process
            if new_process != old_process:
                # Met à jour les modèles de processus si le type de processus a changé
                ModelProcess.objects.filter(
                    Q(process=old_process) | Q(process=new_process)).delete()
                for model_name in project.type_process.nom.split(','):
                    ModelProcess.objects.create(
                        nom=model_name.strip(),
                        process=new_process,
                        projet=projet
                    )
            form.save()
            # Affiche un message de succès
            messages.success(request, 'Projet modifié avec succès..!')
            # Redirige vers la page de détails du projet
            return redirect('detail-projet', pk=projet.pk)
        else:
            # Affiche un message d'erreur si le formulaire n'est pas valide
            messages.success(
                request, 'Quelque chose s\'est pas bien passé...!')
    else:
        # Crée un formulaire de projet pré-rempli avec les données du projet existant
        form = ProjetForm(instance=projet)

    # Rend la page update_projet.html avec le formulaire de projet
    return render(request, 'pages/update_projet.html', context={'form': form, 'projet': projet})


# Vue pour supprimer un projet
@login_required
def deleteProjet(request, pk):
    """
    Vue pour supprimer un projet.
    """
    # Récupère le projet avec l'ID spécifié ou renvoie une erreur 404
    projet = get_object_or_404(Projet, pk=pk)
    # Supprime le projet de la base de données
    projet.delete()
    # Affiche un message de succès
    messages.success(request, 'Projet supprimé avec success..!')
    # Redirige vers la page d'affichage de tous les projets
    return redirect('display')


# ------------------------------ Fin ::: Vues de gestion de projet--------------------------------------


# ----------Debut ::::: Vues de gestion de Categorie / domaine d'activité-------------------
# Vue pour ajouter une catégorie
@login_required
def addCategory(request):
    """
    Vue pour ajouter une catégorie.
    """
    if request.method == 'POST':
        # Crée un formulaire de catégorie avec les données du formulaire POST
        form = CategorieForm(request.POST)
        if form.is_valid():
            # Enregistre la catégorie si le formulaire est valide
            form.save()
            # Affiche un message de succès
            messages.success(request, 'Catégorie ajoutée avec succès...!')
            # Redirige vers la page pour ajouter un client
            return redirect('add-client')
    else:
        # Crée un nouveau formulaire de catégorie
        form = CategorieForm()

    # Rend la page add_category.html avec le formulaire de catégorie
    return render(request, 'pages/add_category.html', context={'form': form})


# Vue pour ajouter un chef de projet
@login_required
def chefProjectView(request):
    """
    Vue pour ajouter un chef de projet.
    """
    if request.method == 'POST':
        # Crée un formulaire de chef de projet avec les données du formulaire POST
        form = ChefProjetForm(request.POST)
        if form.is_valid():
            # Enregistre le chef de projet si le formulaire est valide
            chef_projet = form.save(commit=False)
            chef_projet_in = Chef_de_Projet.objects.filter(
                Chef_de_Projet_mail=chef_projet.Chef_de_Projet_mail).exists()
            user_in = get_user_model().objects.filter(email=chef_projet.Chef_de_Projet_mail,
                                                      groups__name='chef de projet').exists()
            # Génère un mot de passe aléatoire pour le chef de projet
            password = generate_random_password()

            if user_in:
                # Affiche un message d'erreur si l'utilisateur existe déjà
                messages.error(
                    request, f"L'email {chef_projet.Chef_de_Projet_mail} est déjà associé à un chef de projet.")
                return render(request, 'pages/chef_projet.html', {'form': form})
            if chef_projet_in:
                # Affiche un message d'erreur si le chef de projet existe déjà
                messages.error(
                    request, f"Le chef de projet {chef_projet.Chef_de_Projet_name} {chef_projet.Chef_de_Projet_Prenom} est déjà dans la liste des chef de projet avec la meme adresse email {chef_projet.Chef_de_Projet_mail}.")
                return render(request, 'pages/chef_projet.html', {'form': form})

            # Crée un utilisateur et l'associe au chef de projet
            user = get_user_model().objects.create_user(
                email=chef_projet.Chef_de_Projet_mail,
                user_name=chef_projet.Chef_de_Projet_name,
                first_name=chef_projet.Chef_de_Projet_Prenom,
                password=password
            )
            chef_projet.user = user
            chef_projet.save()

            # Ajoute l'utilisateur au groupe 'chef de projet' et lui accorde les permissions nécessaires
            group_name = 'chef de projet'
            group, _ = Group.objects.get_or_create(name=group_name)
            group.user_set.add(user)
            add_permissions_to_group(group_name=group_name)

            # Envoie un email d'invitation au chef de projet avec son mot de passe
            html_message = render_to_string(
                'email/invitation_chef_projet.html', {'user': user, 'password': password})
            subject = 'Vos informations de connexion'
            send_mail(subject, None, settings.EMAIL_HOST_USER, [
                      user.email], html_message=html_message, fail_silently=True)

            # Affiche un message de succès
            messages.success(
                request, f'Chef de projet "{chef_projet.Chef_de_Projet_name}" créé avec succès.')
            # Redirige vers la page pour créer un projet
            return redirect('create-pro')
        else:
            # Affiche un message d'erreur si le formulaire n'est pas valide
            messages.error(request, "Quelque chose s'est très mal passé..!")
    else:
        # Crée un nouveau formulaire de chef de projet
        form = ChefProjetForm()

    # Rend la page chef_projet.html avec le formulaire de chef de projet
    return render(request, 'pages/chef_projet.html', context={'form': form})


# ----------Fin ::::: Vues de gestion Chef de projet-------------------


# ----------Debut ::::: Vues de gestion de Type de processus d'un projet -------------------
# Vue pour ajouter un type de processus
@login_required
def typeProcessView(request):
    """
    Vue pour ajouter un type de processus.
    """
    if request.method == 'POST':
        # Crée un formulaire de type de processus avec les données du formulaire POST
        form = TypeProcessForm(request.POST)
        if form.is_valid():
            # Enregistre le type de processus si le formulaire est valide
            form.save()
            # Affiche un message de succès
            messages.success(request, 'Type de processus créé avec succès...!')
            # Redirige vers la page pour créer un projet
            return redirect('create-pro')
    else:
        # Crée un nouveau formulaire de type de processus
        form = TypeProcessForm()

    # Rend la page add_type_process.html avec le formulaire de type de processus
    return render(request, 'pages/add_type_process.html', context={'form': form})


# Vue pour ajouter une famille de projet
@login_required
def familyProjetView(request):
    """
    Vue pour ajouter une famille de projet.
    """
    if request.method == 'POST':
        # Crée un formulaire de famille de projet avec les données du formulaire POST
        form = FamilyProjetForm(request.POST)
        if form.is_valid():
            # Enregistre la famille de projet si le formulaire est valide
            form.save()
            # Affiche un message de succès
            messages.success(
                request, 'Famille de projet créée avec succès...!')
            # Redirige vers la page pour créer un projet
            return redirect('create-pro')
    else:
        # Crée un nouveau formulaire de famille de projet
        form = FamilyProjetForm()

    # Rend la page family_projet.html avec le formulaire de famille de projet
    return render(request, 'pages/family_projet.html', context={'form': form})


# Vue pour afficher les détails d'un modèle de processus
@login_required
def detailModel(request, pk):
    """
    Vue pour afficher les détails d'un modèle de processus.
    """
    # Vérifie si l'utilisateur est un chef de projet
    is_chef_projet = hasattr(request.user, 'chef_de_projet')
    # Récupère le modèle de processus avec l'ID spécifié ou renvoie une erreur 404
    modelProcess = get_object_or_404(ModelProcess, pk=pk)
    # Récupère les commentaires associés au modèle de processus
    commentaires = Commentaire.objects.filter(model=modelProcess)

    # Récupère le projet associé au modèle de processus
    projet = modelProcess.projet
    context = {
        'model': modelProcess,
        'project': projet,
        'is_chef_projet': is_chef_projet,
        'commentaires': commentaires
    }
    # Rend la page detail_model_process.html avec les détails du modèle de processus
    return render(request, 'pages/detail_model_process.html', context=context)


# Vue pour créer une tâche
@login_required
@permission_required('home.add_tache', raise_exception=True)
def create_task(request, model_id):
    """
    Vue pour créer une tâche.
    """
    # Récupère le modèle de processus associé à la tâche
    model = get_object_or_404(ModelProcess, pk=model_id)
    if request.method == 'POST':
        # Crée un formulaire de tâche avec les données du formulaire POST
        form = TacheForm(request.POST)
        # Récupère le projet associé au modèle de processus
        projet = model.projet

        if form.is_valid():
            # Enregistre la tâche si le formulaire est valide
            tache = form.save(commit=False)
            tache.model = model
            tache.projet = projet
            tache.save()
            messages.success(request, "Tache créée avec succès..!")
            # Redirige vers la page de détails du modèle de processus
            return redirect('detail-model', pk=model_id)
    else:
        # Crée un nouveau formulaire de tâche
        form = TacheForm()

    # Rend la page add_tache.html avec le formulaire de tâche et le modèle de processus associé
    return render(request, 'pages/add_tache.html', {'form': form, 'model': model})


# Vue pour éditer une tâche
@login_required
@permission_required('home.change_tache', raise_exception=True)
def edit_task(request, model_id, task_id):
    """
    Vue pour éditer une tâche.
    """
    # Récupère la tâche avec l'ID spécifié ou renvoie une erreur 404
    task = get_object_or_404(Tache, pk=task_id)
    # Récupère le modèle de processus associé à la tâche
    model = get_object_or_404(ModelProcess, pk=model_id)
    if request.method == 'POST':
        # Crée un formulaire de tâche pré-rempli avec les données de la tâche existante
        form = TacheForm(request.POST, instance=task)
        if form.is_valid():
            # Enregistre les modifications de la tâche si le formulaire est valide
            form.save()
            # Redirige vers la page de détails du modèle de processus
            return redirect('detail-model', pk=model_id)
    else:
        # Crée un formulaire de tâche pré-rempli avec les données de la tâche existante
        form = TacheForm(instance=task)

    # Rend la page modifie_acheve.html avec le formulaire de tâche et le modèle de processus associé
    return render(request, 'pages/modifie_acheve.html', {'form': form, 'model': model})


def delete_task(request, model_id, task_id):
    model = get_object_or_404(ModelProcess, pk=model_id)
    tache = get_object_or_404(Tache, pk=task_id)
    tache.delete()
    messages.success(request, "Tache Supprimée avec succès")
    return redirect('detail-model', pk=model_id)

# Vue pour ajouter un commentaire à un modèle de processus


@login_required
def ajouter_commentaire(request, model_id):
    """
    Vue pour ajouter un commentaire à un modèle de processus.
    """
    if request.method == 'POST':
        # Crée un formulaire de commentaire avec les données du formulaire POST
        form = CommentaireForm(request.POST)
        if form.is_valid():
            # Récupère le contenu du commentaire
            contenu = form.cleaned_data['contenu']
            # Récupère l'utilisateur connecté comme créateur du commentaire
            creator = request.user
            # Récupère le modèle de processus associé au commentaire
            model = ModelProcess.objects.get(pk=model_id)
            # Crée un nouvel objet Commentaire
            Commentaire.objects.create(
                contenu=contenu, creator=creator, model=model)
            # Redirige vers la page de détails du modèle de processus
            return redirect('detail-model', pk=model_id)
    else:
        # Crée un nouveau formulaire de commentaire
        form = CommentaireForm()

    # Rend la page detail_model_process.html avec le formulaire de commentaire
    return render(request, 'pages/detail_model_process.html', {'form': form})
