from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window  
from kivy.graphics import Color, Ellipse, Rectangle, Rotate
import re
import math

# 🔥 Variables globales
TARIF_PAR_MEGA = 10
consommation1 = 0
consommation2 = 0
solde = 0
consommation_active = False
destinataire = "+22605455024"
vitesse_consommation = 5  # Par défaut 5 Mo/s
code_pays = "+226"


class AnimationWidget(Widget):
    """ 🎨 Zone contenant le cercle et le carré animé """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0  # Angle de rotation du carré
        self.rotation = None
        
        with self.canvas:
            # 🔵 Dessin du cercle
            Color(0, 0, 1, 0.5)  # Bleu semi-transparent
            self.cercle = Ellipse(size=(300, 300), pos=self.center)
            
            # 🔲 Dessin du carré
            Color(1, 1, 1, 1)  # Blanc
            self.rotation = Rotate(angle=self.angle, origin=self.center)
            self.carre = Rectangle(size=(100, 100), pos=self.center)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        """ 🖌️ Met à jour les positions du cercle et du carré """
        cercle_x = self.center_x - 150
        cercle_y = self.center_y - 150
        self.cercle.pos = (cercle_x, cercle_y)

        carre_x = self.center_x - 50
        carre_y = self.center_y - 50
        self.carre.pos = (carre_x, carre_y)
        self.rotation.origin = (self.center_x, self.center_y)

    def rotate_square(self, dt):
        """ 🔄 Fait tourner le carré """
        self.angle += 5  # Augmente l'angle
        self.rotation.angle = self.angle
        self.canvas.ask_update()
        
class RKiSSApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 🔹 Barre supérieure (RX + Solde + Retirer)
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))

        self.btn_rx = Button(text="RX", font_size=16, size_hint=(0.2, 1), background_color=(0, 0, 1, 1))
        self.btn_rx.bind(on_press=self.ouvrir_menu_rx)
        top_layout.add_widget(self.btn_rx)

        self.label_solde = Label(text="Solde : 0 FCFA", font_size=18, size_hint=(0.6, 1))
        top_layout.add_widget(self.label_solde)

        self.btn_retirer = Button(text="Retirer", font_size=16, size_hint=(0.2, 1), background_color=(1, 0, 0, 1))
        self.btn_retirer.bind(on_press=self.ouvrir_retrait)
        top_layout.add_widget(self.btn_retirer)

        self.root.add_widget(top_layout)

        # 🔹 Labels des consommations
        self.label_conso1 = Label(text="Consommation 1 : 0 Mo", font_size=16, size_hint=(1, 0.1))
        self.root.add_widget(self.label_conso1)

        self.label_conso2 = Label(text="Consommation 2 : 0 Mo", font_size=16, size_hint=(1, 0.1))
        self.root.add_widget(self.label_conso2)
        
        
        # 🔹 Zone d'animation (cercle et carré)
        self.animation_widget = AnimationWidget()
        self.root.add_widget(self.animation_widget)

        # 🔹 Bouton Démarrer/Arrêter
        self.btn_demarrer = Button(text="Démarrer", font_size=20, size_hint=(1, 0.15), background_color=(0, 1, 0, 1))
        self.btn_demarrer.bind(on_press=self.demarrer_consommation)
        

        self.root.add_widget(Widget(size_hint=(1, 0.45)))
        self.root.add_widget(self.btn_demarrer)

        Clock.schedule_interval(self.mise_a_jour_conso, 1)
        return self.root

    def ouvrir_menu_rx(self, instance):
        """ 🔄 Menu pour changer la vitesse de consommation """
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)

        btn_x2 = Button(text="X2", on_press=lambda x: self.changer_vitesse(10))
        btn_x3 = Button(text="X3", on_press=lambda x: self.changer_vitesse(15))
        btn_x4 = Button(text="X4", on_press=lambda x: self.changer_vitesse(20))

        box.add_widget(btn_x2)
        box.add_widget(btn_x3)
        box.add_widget(btn_x4)

        self.popup_rx = Popup(title="Réglage consommation", content=box, size_hint=(0.5, 0.4))
        self.popup_rx.open()

    def changer_vitesse(self, nouvelle_vitesse):
        """ ⚡ Change la vitesse de consommation """
        global vitesse_consommation
        vitesse_consommation = nouvelle_vitesse
        self.popup_rx.dismiss()
             
    def demarrer_consommation(self, instance):
        """ ▶️ Démarre ou arrête la consommation """
        global consommation_active
        consommation_active = not consommation_active

        if consommation_active:
            self.btn_demarrer.text = "Arrêter"
            self.btn_demarrer.background_color = (1, 0, 0, 1)
            Clock.schedule_interval(self.augmenter_consommation, 1)
        else:
            self.btn_demarrer.text = "Démarrer"
            self.btn_demarrer.background_color = (0, 1, 0, 1)
            Clock.unschedule(self.augmenter_consommation)
            

    def augmenter_consommation(self, dt):
        """ 📈 Augmente les consommations et convertit en argent après 100 Mo """
        global consommation1, consommation2, solde

        consommation1 += vitesse_consommation
        consommation2 += vitesse_consommation

        if consommation1 >= 100:
            self.convertir_en_argent(100)
            consommation1 -= 100

        if consommation2 >= 100:
            self.convertir_en_argent(100)
            consommation2 -= 100

    def convertir_en_argent(self, mo):
        """ 💰 Convertit les Mo en FCFA """
        global solde
        montant_total = mo * TARIF_PAR_MEGA
        solde += montant_total * 0
        print(f"Montant envoyé ({destinataire}): {montant_total * 1} FCFA")
        

    def mise_a_jour_conso(self, dt):
        """ 🔄 Met à jour l'affichage """
        self.label_conso1.text = f"progrètion : {consommation1} %"
        self.label_conso2.text = f"progrètion : {consommation2} %"
        self.label_solde.text = f"Solde : {solde} FCFA"

    def ouvrir_retrait(self, instance):
        """ 💳 Ouvre la fenêtre de retrait """
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)

        btn_numero = Button(text="Numéro", on_press=self.ouvrir_retrait_numero)
        btn_carte = Button(text="Carte bancaire", on_press=self.ouvrir_retrait_carte)
        btn_annuler = Button(text="Annuler", on_press=lambda x: self.popup_retrait.dismiss())

        box.add_widget(btn_numero)
        box.add_widget(btn_carte)
        box.add_widget(btn_annuler)

        self.popup_retrait = Popup(title="Retrait", content=box, size_hint=(0.5, 0.4))
        self.popup_retrait.open()

    def ouvrir_retrait_numero(self, instance):
        """ 📲 Saisie du numéro de téléphone et retrait """
        def valider():
            numero = self.entry_telephone.text
            if re.match(r"^\+\d{8,15}$", numero):
                self.effectuer_retrait(numero)
                self.popup_numero.dismiss()

        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.entry_telephone = TextInput(text=code_pays, multiline=False)

        btn_ok = Button(text="OK", on_press=lambda x: valider())
        btn_annuler = Button(text="Annuler", on_press=lambda x: self.popup_numero.dismiss())

        box.add_widget(self.entry_telephone)
        box.add_widget(btn_ok)
        box.add_widget(btn_annuler)

        self.popup_numero = Popup(title="Retrait via SIM", content=box, size_hint=(0.7, 0.4))
        self.popup_numero.open()

    def ouvrir_retrait_carte(self, instance):
        """ 💳 Saisie de la carte bancaire pour retrait """
        def valider():
            carte = self.entry_carte.text
            if re.match(r"^\d{16}$", carte):  # Vérification d'un numéro de carte simple (16 chiffres)
                self.effectuer_retrait(carte)
                self.popup_carte.dismiss()

        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.entry_carte = TextInput(text="", multiline=False)

        btn_ok = Button(text="OK", on_press=lambda x: valider())
        btn_annuler = Button(text="Annuler", on_press=lambda x: self.popup_carte.dismiss())

        box.add_widget(self.entry_carte)
        box.add_widget(btn_ok)
        box.add_widget(btn_annuler)

        self.popup_carte = Popup(title="Retrait via Carte Bancaire", content=box, size_hint=(0.7, 0.4))
        self.popup_carte.open()

    def effectuer_retrait(self, destinataire):
        """ 💰 Effectue le transfert et remet le solde à zéro """
        global solde
        print(f"Transfert de {solde} FCFA vers {destinataire}")
        solde = 0
        self.mise_a_jour_conso(0)
    

if __name__ == "__main__":
    RKiSSApp().run()
