from django.contrib import admin
from .models import Chef_de_Projet, Responsable_Projet, Equipe_de_Projet, Teams_Projet, Categorie, genre, \
    Cycle_de_devellopement, Cycle_de_vie, Etape, sequence, Livrable, document, Client, customer, Famille_de_Projet, \
    Family, Projet, programme, Site, emplacement, Avancement, Progression, Equipements, outillage

admin.site.register(Chef_de_Projet,Responsable_Projet)
admin.site.register(Equipe_de_Projet,Teams_Projet)
admin.site.register(Categorie,genre)
admin.site.register(Cycle_de_devellopement,Cycle_de_vie)
admin.site.register(Livrable,document)
admin.site.register(Etape,sequence)
admin.site.register(Client,customer)
admin.site.register(Famille_de_Projet,Family)
admin.site.register(Projet,programme)
admin.site.register(Site,emplacement)
admin.site.register(Avancement,Progression)
admin.site.register(Equipements,outillage)
admin.site.site_header="ACTIA"
admin.site.site_title="ACTIA"


