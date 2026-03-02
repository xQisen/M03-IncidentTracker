from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from core.models import SecurityIncident
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
@login_required  # Aquesta línia protegeix la vista. Sense sessió, no passes.
def perfil_usuari(request):
    return render(request, 'perfil.html')
# Create your views here.
@login_required
def cerca_incidents_vulnerable(request):
    """
    Versió SEGURA - Utilitza l'ORM de Django en lloc de SQL concatenat
    """
    resultats = []
    query = ""
    
    if request.method == "GET" and request.GET.get('q'):
        query = request.GET.get('q', '')
        
        # ✅ SEGUR: L'ORM de Django parametritza automàticament
        # Utilitzem Q objects per fer cerques complexes
        incidents = SecurityIncident.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).values('id', 'title', 'description', 'severity', 'detected_at')
        
        # Convertim a llista per mantenir compatibilitat amb la plantilla
        resultats = [
            (i['id'], i['title'], i['description'], i['severity'], i['detected_at']) 
            for i in incidents
        ]
    
    return render(request, 'cerca_vulnerable.html', {
        'resultats': resultats,
        'query': query,
        'error': None  # Ja no hi ha errors SQL
    })

@login_required
def actualitzar_email_vulnerable(request):
    """
    Versió SEGURA - Utilitza l'ORM de Django en lloc de SQL concatenat
    """
    missatge = ""
    email_actual = request.user.email
    
    if request.method == "POST":
        email = request.POST.get('email', '')
        
        try:
            # ✅ SEGUR: L'ORM de Django parametritza automàticament
            # Actualització segura directa a l'objecte User
            request.user.email = email
            request.user.save()
            
            missatge = "✅ Email actualitzat correctament (versió segura amb ORM)"
            
        except Exception as e:
            missatge = f"❌ Error: {str(e)}"
    
    return render(request, 'actualitzar_email.html', {
        'missatge': missatge,
        'usuari': request.user,
        'email_actual': email_actual
    })
@login_required
def detall_incident_segur(request, incident_id):
    """
    Versió SEGURA - Implementa control d'accés a nivell de fila
    Només mostra l'incident si l'usuari n'és el propietari
    """
    try:
        # ✅ SEGUR: Filtrem per id I per usuari
        incident = SecurityIncident.objects.get(
            id=incident_id,
            usuari=request.user  # 🔴 CLAU: Control d'accés!
        )
        
        return render(request, 'detall_incident_segur.html', {
            'incident': incident,
            'usuari_actual': request.user.username
        })
    except SecurityIncident.DoesNotExist:
        # Retornem 404 per no donar pistes
        from django.http import Http404
        raise Http404("L'incident no existeix o no tens permís per veure'l")



@login_required
def llistar_incidents_xss(request):
    """
    Vista per demostrar XSS - MOSTRA ELS INCIDENTS AMB |safe (VULNERABLE)
    """
    incidents = SecurityIncident.objects.all()
    
    return render(request, 'llistar_incidents_xss.html', {
        'incidents': incidents
    })

@login_required
def llistar_incidents_segur(request):
    """
    Vista per demostrar XSS - MOSTRA ELS INCIDENTS SENSE |safe (SEGUR)
    """
    incidents = SecurityIncident.objects.all()
    
    return render(request, 'llistar_incidents_segur.html', {
        'incidents': incidents
    })
