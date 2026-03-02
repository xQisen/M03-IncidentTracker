from django.contrib import admin
from django.urls import path, include
from core.views import perfil_usuari, cerca_incidents_vulnerable, actualitzar_email_vulnerable, detall_incident_segur, llistar_incidents_xss, llistar_incidents_segur

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('perfil/', perfil_usuari, name='perfil'),
    path('cerca-vulnerable/', cerca_incidents_vulnerable, name='cerca_vulnerable'),
    path('actualitzar-email/', actualitzar_email_vulnerable, name='actualitzar_email'),
    path('incident-segur/<int:incident_id>/', detall_incident_segur, name='detall_incident_segur'),
    path('xss-demo/', llistar_incidents_xss, name='llistar_incidents_xss'),
    path('xss-segur/', llistar_incidents_segur, name='llistar_incidents_segur'),
]
