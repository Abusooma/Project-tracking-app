from django import forms
from .models import *


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

        self.Domaine_dactivite = Categorie.objects.all()

        self.domaine_choices = [('', '-- Choisir un domaine d\'activité --')]
        for domaine in self.Domaine_dactivite:
            self.domaine_choices.append((domaine.iddomaine_dactivite, domaine.Domaine_dactivite))

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control mb-3 mt-1 border border-lg border-dark px-1'})

        self.fields['Domaine_dactivite'] = forms.ChoiceField(
            choices=self.domaine_choices,
            widget=forms.Select(attrs={'class': 'form-control mb-1 mt-1 border px-1 border-lg border-dark'})
        )

    def clean_Domaine_dactivite(self):
        domaine_id = self.cleaned_data['Domaine_dactivite']
        return Categorie.objects.get(pk=domaine_id)

    class Meta:
        model = Client
        fields = ['Nom_Client', 'Adresse', 'Domaine_dactivite']


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['Domaine_dactivite']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;'})


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['nom', 'type_process', 'Date_debut', 'Date_fin', 'description', 'nom_client', 'chef_de_projet',
                  'famille_projet']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;'})

        self.fields['description'].widget = forms.Textarea(
            attrs={'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;', 'rows': 3, 'cols': 40})

        # Personnalisation du formulaire de type de processus

        self.type_process = Process.objects.all()
        self.process_choices = [('', '-- Choisir un type de processus --')]

        for process in self.type_process:
            self.process_choices.append((process.id, process.nom))

        self.fields['type_process'] = forms.ChoiceField(
            choices=self.process_choices,
            widget=forms.Select(attrs={'class': 'form-control mb-1 mt-1 border px-1'})
        )

        # Personnalisation du formulaire de client
        self.clients = Client.objects.all()
        self.client_choices = [('', '-- Choisir un client --')]

        for client in self.clients:
            self.client_choices.append((client.idClient, client.Nom_Client))

        self.fields['nom_client'] = forms.ChoiceField(
            choices=self.client_choices,
            widget=forms.Select(attrs={'class': 'form-control mb-1 mt-1 border px-1'})
        )

        # Personnalisation du formulaire de chef de projet

        self.chef_projets = Chef_de_Projet.objects.all()
        self.chef_projets_choices = [('', '-- Choisir un RPI --')]

        for chef_projet in self.chef_projets:
            self.chef_projets_choices.append((chef_projet.idChef_de_Projet, chef_projet.Chef_de_Projet_name))

        self.fields['chef_de_projet'] = forms.ChoiceField(
            choices=self.chef_projets_choices,
            widget=forms.Select(attrs={'class': 'form-control mb-1 mt-1 border px-1'})
        )

        # Personnalisation du formulaire de famille de projet

        self.familles = Famille_de_Projet.objects.all()
        self.famille_choices = [('', '-- Choisir une Famille de projet --')]

        for famille in self.familles:
            self.famille_choices.append((famille.idFamille, famille.Nom_Famille))

        self.fields['famille_projet'] = forms.ChoiceField(
            choices=self.famille_choices,
            widget=forms.Select(attrs={'class': 'form-control mb-1 mt-1 border px-1'})
        )

    def clean_type_process(self):
        type_process_id = self.cleaned_data['type_process']
        return Process.objects.get(pk=type_process_id)

    def clean_nom_client(self):
        client_id = self.cleaned_data['nom_client']
        return Client.objects.get(idClient=client_id)

    def clean_chef_de_projet(self):
        chef_id = self.cleaned_data['chef_de_projet']
        return Chef_de_Projet.objects.get(idChef_de_Projet=chef_id)

    def clean_famille_projet(self):
        famille_id = self.cleaned_data['famille_projet']
        return Famille_de_Projet.objects.get(idFamille=famille_id)


class ChefProjetForm(forms.ModelForm):
    class Meta:
        model = Chef_de_Projet
        fields = ['Chef_de_Projet_name', 'Chef_de_Projet_Prenom', 'Chef_de_Projet_mail']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;'})


class TypeProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['nom']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;'})


class FamilyProjetForm(forms.ModelForm):
    class Meta:
        model = Famille_de_Projet
        fields = ['Nom_Famille']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;'})


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ['description', 'date_achevement', 'acheve']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control px-2', 'style': 'border: 1px solid #ced4da;'}),
            'date_achevement': forms.DateInput(
                attrs={'class': 'form-control datepicker-border px-2', 'style': 'border: 1px solid #ced4da;'}),
            'acheve': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border: 1px solid #ced4da;'})
        }


class ModelProcessForm(forms.ModelForm):
    class Meta:
        model = ModelProcess
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'style': 'border: 1px solid #ced4da;'})
        }


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
