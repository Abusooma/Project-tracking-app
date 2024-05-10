from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # urls de gestion de categorie/ domaine d'activité
    path('domaine/', views.addCategory, name='category'),

    # urls de gestion de chef de projet
    path('add-chef-projet/', views.chefProjectView, name='add-chef-projet'),

    # urls de gestion de type de process du projet
    path('type-process/', views.typeProcessView, name='type-process'),

    # urls de gestion de famille de projet
    path('famille-projet/', views.familyProjetView, name='family-projet'),

    # urls de gestion de client
    path('clients/', views.clientView, name='clients'),
    path('add-client/', views.create_client, name='add-client'),
    path('update-client/<int:pk>/', views.update_client, name='update-client'),
    path('delete-client/<int:pk>/', views.deleteClient, name='delete-client'),

    # urls de gestion de projet
    path('display-project/', views.display_all_project, name='display'),
    path('project/', views.createProject, name='create-pro'),
    path('detail/projet/<int:pk>/', views.detailProject, name='detail-projet'),
    path('update/projet/<int:pk>/', views.updateProject, name='update-projet'),
    path('delete/projet/<int:pk>/', views.deleteProjet, name='delete-projet'),

    # urls de gestion des taches

    path('model/<int:pk>', views.detailModel, name='detail-model'),

    path('create-task/<int:model_id>/', views.create_task, name='create-task'),
    path('task/<int:model_id>/<int:task_id>/', views.edit_task, name='modify-task'),
    path('delete/<int:model_id>/<int:task_id>/', views.delete_task, name='delete-task'),

    path('commentaire/<int:model_id>/', views.ajouter_commentaire, name='ajouter_commentaire'),
]
