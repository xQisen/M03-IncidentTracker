from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import time

class SecurityVulnerabilityTest(TestCase):
    """
    Test per detectar la vulnerabilitat d'escalada de privilegis via SQLi
    Aquest test HA DE FALLAR inicialment - demostra que detectem el forat
    """
    
    def setUp(self):
        """Preparació de l'entorn de test"""
        # Creem un client per fer peticions HTTP
        self.client = Client()
        
        # Creem un usuari normal (NO superusuari)
        self.analista = User.objects.create_user(
            username='analista_test',
            password='password123',
            email='analista@test.com'
        )
        self.analista.is_superuser = False
        self.analista.save()
        
        print("\n🔧 SETUP COMPLETAT:")
        print(f"   - Usuari creat: {self.analista.username}")
        print(f"   - És superusuari: {self.analista.is_superuser}")
        print(f"   - ID: {self.analista.id}")
    
    def test_sql_injection_privilege_escalation(self):
        """
        TEST QUE HA DE FALLAR (Fail-First)
        Simula l'atac SQLi i verifica que l'usuari NO es converteix en superusuari
        En estat vulnerable, aquest test FALLARÀ perquè l'atac funciona
        """
        
        # 1. Fem login amb l'usuari analista
        login_success = self.client.login(
            username='analista_test', 
            password='password123'
        )
        self.assertTrue(login_success, "❌ No s'ha pogut fer login")
        print("\n✅ Login exitós com a analista_test")
        
        # 2. Verifiquem l'estat ABANS de l'atac
        usuari_abans = User.objects.get(id=self.analista.id)
        print(f"\n📊 ESTAT ABANS DE L'ATAC:")
        print(f"   - Usuari: {usuari_abans.username}")
        print(f"   - És superusuari: {usuari_abans.is_superuser}")
        print(f"   - Email: {usuari_abans.email}")
        
        # 3. PAYLOAD MALICIÓS - Adaptat per a booleans
        # Aquest payload intenta convertir l'usuari en superusuari
        payload = f"', is_superuser = TRUE WHERE id = {self.analista.id}; --"
        
        print(f"\n💣 EXECUTANT ATAC SQLi:")
        print(f"   - Payload: {payload}")
        print(f"   - URL: /actualitzar-email/")
        
        # 4. Enviem la petició POST vulnerable
        response = self.client.post(
            reverse('actualitzar_email'),  # La URL de la vista vulnerable
            {'email': payload},
            follow=True
        )
        
        # 5. Verifiquem que la petició ha anat bé
        self.assertEqual(response.status_code, 200, 
                        f"❌ Error en la petició: {response.status_code}")
        print(f"\n📨 RESPOSTA HTTP: {response.status_code}")
        
        # 6. 🔴 🔴 🔴 AQUEST ÉS EL TEST CRÍTIC 🔴 🔴 🔴
        # Recuperem l'usuari actualitzat de la base de dades
        usuari_despres = User.objects.get(id=self.analista.id)
        
        print(f"\n📊 ESTAT DESPRÉS DE L'ATAC:")
        print(f"   - Usuari: {usuari_despres.username}")
        print(f"   - És superusuari: {usuari_despres.is_superuser}")
        print(f"   - Email: {usuari_despres.email}")
        
        # 🔴 AQUEST ASSERT HA DE FALLAR MENTRE LA VULNERABILITAT EXISTEIXI
        print("\n🔴 EXECUTANT ASSERT CRÍTIC (hauria de FALLAR)...")
        self.assertFalse(
            usuari_despres.is_superuser,
            f"❌ TEST FALLAT: L'usuari s'ha convertit en superusuari! "
            f"La vulnerabilitat existeix i permet escalada de privilegis.\n"
            f"   Abans: is_superuser={usuari_abans.is_superuser}\n"
            f"   Després: is_superuser={usuari_despres.is_superuser}"
        )
        
        # Si arribem aquí, el test passaria (PERÒ NO HA DE PASSAR)
        print("\n✅ TEST PASSAT (AIXÒ ÉS INESPERAT!):")
        print("   L'atac NO ha funcionat. La vulnerabilitat està corregida?")
    
    def test_payload_variants(self):
        """Test amb diferents variants del payload"""
        
        self.client.login(username='analista_test', password='password123')
        
        # Llista de payloads per provar
        payloads = [
            f"', is_superuser = TRUE WHERE id = {self.analista.id}; --",
            f"', is_superuser = 't' WHERE id = {self.analista.id}; --",
            f"', is_superuser = 1::boolean WHERE id = {self.analista.id}; --",
            f"', is_superuser = true WHERE id = {self.analista.id}; --",
        ]
        
        for i, payload in enumerate(payloads, 1):
            print(f"\n📝 Provant payload {i}: {payload}")
            
            # Guardem estat abans
            usuari_abans = User.objects.get(id=self.analista.id)
            abans_super = usuari_abans.is_superuser
            
            # Enviem payload
            response = self.client.post(
                reverse('actualitzar_email'),
                {'email': payload}
            )
            
            # Comprovem estat després
            usuari_despres = User.objects.get(id=self.analista.id)
            despres_super = usuari_despres.is_superuser
            
            if abans_super != despres_super:
                print(f"   ⚠️ CANVI DETECTAT! is_superuser: {abans_super} → {despres_super}")
                print(f"   🔴 Payload {i} HA FUNCIONAT!")
            
            # Restablim l'estat original per al següent test
            if despres_super:
                usuari_despres.is_superuser = False
                usuari_despres.save()
