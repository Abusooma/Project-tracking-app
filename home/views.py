from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMultiAlternatives, send_mail
from core import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.core.paginator import Paginator
from .utils import generate_random_password, add_permissions_to_group


def index(request):
    return render(request, 'pages/index.html')


def clientView(request):
    all_clients = Client.objects.all()
    clients_per_page = 5
    paginator = Paginator(all_clients, clients_per_page)
    page_number = request.GET.get('page', 1)
    clients = paginator.get_page(page_number)

    return render(request, 'pages/clients.html', context={'clients': clients})


# -----------------------Debut :::: Vues de gestion de client------------------------

def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client ajouté avec succès!')
            return redirect('clients')
    else:
        form = ClientForm()
    return render(request, 'pages/add_client.html', {'form': form})


def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client modifié avec success..!')
            return redirect('clients')
        else:
            messages.error(request, 'Quelque chose s\'est mal passé')
    else:
        form = ClientForm(instance=client)

    return render(request, 'pages/update_client.html', context={'form': form})


def deleteClient(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    messages.success(request, 'Client supprimé avec success...!')
    return redirect('clients')


# ------------------------------Fin::::: Vues de gestion de client -----------------------------


# --------------------------Debut :::::: Vues de gestion de projet------------------------------

@login_required
def display_all_project(request):
    query = request.GET.get('query', '')
    all_projects = Projet.objects.filter(
        Q(nom__icontains=query) | Q(description__icontains=query)
    )

    is_chef_projet = hasattr(request.user, 'chef_de_projet')
    if is_chef_projet:
        all_projects = all_projects.filter(chef_de_projet=request.user.chef_de_projet)

    projects_per_page = 7
    paginator = Paginator(all_projects, projects_per_page)
    page_number = request.GET.get('page', 1)
    projects = paginator.get_page(page_number)
    context = {
        'projects': projects,
        'query': query,
        'all_projects': all_projects,
        'is_chef_projet': is_chef_projet
    }
    return render(request, 'admin/dashboard_display.html', context=context)


def createProject(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            form.save()
            chef_de_projet = projet.chef_de_projet
            subject = 'Nouveau projet assigné'
            html_content = render_to_string('email/projet_assigne.html',
                                            {'chef_de_projet': chef_de_projet, 'projet': projet})
            email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [chef_de_projet.Chef_de_Projet_mail])
            email.attach_alternative(html_content, 'text/html')
            email.send()

            for model_name in projet.type_process.nom.split(', '):
                ModelProcess.objects.create(
                    nom=model_name.strip(),
                    process=projet.type_process,
                    projet=projet
                )
            messages.success(request, 'Projet créé avec succès..!')
            return redirect('display')
    else:
        form = ProjetForm()

    return render(request, 'pages/creer_project.html', {'form': form})


def detailProject(request, pk):
    project = get_object_or_404(Projet, pk=pk)
    modeles = ModelProcess.objects.filter(projet=project)
    return render(request, 'pages/detail_project.html', context={'projet': project, 'modeles': modeles})


def updateProject(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    old_process = projet.type_process
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            project = form.save(commit=False)
            new_process = project.type_process
            if new_process != old_process:
                ModelProcess.objects.filter(Q(process=old_process) | Q(process=new_process)).delete()
                for model_name in project.type_process.nom.split(','):
                    ModelProcess.objects.create(
                        nom=model_name.strip(),
                        process=new_process,
                        projet=projet
                    )

            form.save()
            messages.success(request, 'Projet modifié avec succès..!')
            return redirect('detail-projet', pk=projet.pk)
        else:
            messages.success(request, 'Quelque chose s\'est pas bien passé...!')
    else:
        form = ProjetForm(instance=projet)

    return render(request, 'pages/update_projet.html', context={'form': form, 'projet': projet})


def deleteProjet(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    projet.delete()
    messages.success(request, 'Projet supprimé avec success..!')
    return redirect('display')


# ------------------------------ Fin ::: Vues de gestion de projet--------------------------------------


# ----------Debut ::::: Vues de gestion de Categorie / domaine d'activité-------------------
def addCategory(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categorie ajouté avec succèss...!')
            return redirect('add-client')
    else:
        form = CategorieForm()

    return render(request, 'pages/add_category.html', context={'form': form})


# ----------Fin ::::: Vues de gestion de Categorie / domaine d'activité-------------------


# ----------Debut ::::: Vues de gestion Chef de projet-------------------
def chefProjectView(request):
    if request.method == 'POST':
        form = ChefProjetForm(request.POST)
        if form.is_valid():
            chef_projet = form.save(commit=False)

            password = generate_random_password()

            if get_user_model().objects.filter(email=chef_projet.Chef_de_Projet_mail,
                                               groups__name='chef de projet').exists():
                messages.error(request,
                               f"L'email {chef_projet.Chef_de_Projet_mail} est déjà associé à un chef de projet.")
                return render(request, 'pages/chef_projet.html', {'form': form})

            user = get_user_model().objects.create_user(
                email=chef_projet.Chef_de_Projet_mail,
                user_name=chef_projet.Chef_de_Projet_name,
                first_name=chef_projet.Chef_de_Projet_Prenom,
                password=password
            )

            chef_projet.user = user
            chef_projet.save()
            group_name = 'chef de projet'
            group, _ = Group.objects.get_or_create(name=group_name)
            group.user_set.add(user)

            add_permissions_to_group(group_name=group_name)

            # Envoyer un email d'invitation
            html_message = render_to_string('email/invitation_chef_projet.html', {'user': user, 'password': password})
            subject = 'Vos informations de connexion'
            send_mail(subject, None, settings.EMAIL_HOST_USER, [user.email], html_message=html_message)

            messages.success(request, f'Chef de projet "{chef_projet.Chef_de_Projet_name}" créé avec succès.')

            return redirect('create-pro')
        else:
            messages.error(request, "Quelque chose s'est très mal passé..!")
    else:
        form = ChefProjetForm()

    return render(request, 'pages/chef_projet.html', context={'form': form})


# ----------Fin ::::: Vues de gestion Chef de projet-------------------


# ----------Debut ::::: Vues de gestion de Type de processus d'un projet -------------------

def typeProcessView(request):
    if request.method == 'POST':
        form = TypeProcessForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ' type de process créé avec success...!')
            return redirect('create-pro')
    else:
        form = TypeProcessForm()

    return render(request, 'pages/add_type_process.html', context={'form': form})


def familyProjetView(request):
    if request.method == 'POST':
        form = FamilyProjetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ' Famille de projet créé avec success...!')
            return redirect('create-pro')
    else:
        form = FamilyProjetForm()

    return render(request, 'pages/family_projet.html', context={'form': form})


# ----------Fin ::::: Vues de gestion de Type de processus d'un projet -------------------

def detailModel(request, pk):
    is_chef_projet = request.user.groups.filter(name='chef de projet').exists()
    modelProcess = get_object_or_404(ModelProcess, pk=pk)
    commentaires = Commentaire.objects.filter(model=modelProcess)

    projet = modelProcess.projet
    context = {
        'model': modelProcess,
        'project': projet,
        'is_chef_projet': is_chef_projet,
        'commentaires': commentaires
    }
    return render(request, 'pages/detail_model_process.html', context=context)


@login_required
@permission_required('home.add_tache', raise_exception=True)
def create_task(request, model_id):
    model = get_object_or_404(ModelProcess, pk=model_id)
    projet = model.projet

    if request.method == 'POST':
        form = TacheForm(request.POST)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.model = model
            tache.projet = projet
            tache.save()
            return redirect('detail-model', pk=model_id)
    else:
        form = TacheForm()
    return render(request, 'pages/add_tache.html', {'form': form, 'model': model})


@login_required
@permission_required('home.change_tache', raise_exception=True)
def edit_task(request, model_id, task_id):
    task = get_object_or_404(Tache, pk=task_id)
    model = get_object_or_404(ModelProcess, pk=model_id)
    if request.method == 'POST':
        form = TacheForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('detail-model', pk=model_id)
    else:
        form = TacheForm(instance=task)

    return render(request, 'pages/modifie_acheve.html', {'form': form, 'model': model})


def ajouter_commentaire(request, model_id):
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            contenu = form.cleaned_data['contenu']
            creator = request.user
            model = ModelProcess.objects.get(pk=model_id)
            Commentaire.objects.create(contenu=contenu, creator=creator, model=model)

            return redirect('detail-model', pk=model_id)
    else:
        form = CommentaireForm()
    return render(request, 'pages/detail_model_process.html', {'form': form})
