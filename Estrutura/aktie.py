import datetime
from plyer import notification
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from kivy.clock import Clock

__version__ = ("BETA")


# Configuração do Firebase
cred = credentials.Certificate("C:/Users/felli/Documents/projetox/projetinho1/aktiecloudfirestonekey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class ValidadeApp(App):
    def build(self):
        self.produtos = []  # Lista para armazenar os produtos localmente
        
        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

           # Layout de ancoragem para a versão
        self.anchor_layout = AnchorLayout(size_hint=(1, 1), anchor_x='right', anchor_y='bottom')

        # Criando o Label para a versão
        self.version_label = Label(
            text=f"Versão: {__version__}",
            font_size=10,  # Tamanho
            opacity=0.3,   # Transparência (0.0 a 1.0)
            color=(1, 1, 1, 1),  # Cor do texto (branco)
            size_hint=(None, None),
            size=(Window.width * 0.2, Window.height * 0.1)  # Tamanho proporcional à tela
        )

        # Adicionando o Label à AnchorLayout
        self.anchor_layout.add_widget(self.version_label)

        # Adicionando o AnchorLayout ao layout principal
        self.layout.add_widget(self.anchor_layout)
        
        # Campos de entrada
        self.produto_label = Label(text="Digite o nome do produto:")
        self.layout.add_widget(self.produto_label)
        
        self.produto_input = TextInput(multiline=False)
        self.layout.add_widget(self.produto_input)
        
        self.validade_label = Label(text="Digite a validade (dd/mm/aaaa):")
        self.layout.add_widget(self.validade_label)
        
        self.validade_input = TextInput(multiline=False)
        self.layout.add_widget(self.validade_input)
        
        # Botões
        self.add_button = Button(text="Adicionar produto")
        self.add_button.bind(on_press=self.adicionar_produto)
        self.layout.add_widget(self.add_button)
        
        self.check_button = Button(text="Verificar validade")
        self.check_button.bind(on_press=self.verificar_produtos)
        self.layout.add_widget(self.check_button)
        
        # Lista de produtos
        self.produtos_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.produtos_layout.bind(minimum_height=self.produtos_layout.setter('height'))
        
        self.scroll_view = ScrollView()
        self.scroll_view.add_widget(self.produtos_layout)
        self.layout.add_widget(self.scroll_view)
        
        # Carrega os produtos do Firestore ao iniciar
        Clock.schedule_once(lambda dt: self.carregar_produtos(), 0)
        
        return self.layout
    
    def carregar_produtos(self):
        """Carrega os produtos do Firestore e exibe na interface"""
        try:
            # Limpa a lista local e a interface
            self.produtos = []
            self.produtos_layout.clear_widgets()
            
            # Busca os produtos no Firestore
            docs = db.collection('produtos').stream()
            
            for doc in docs:
                produto_data = doc.to_dict()
                produto = produto_data.get('nome', '')
                validade = produto_data.get('validade', '')
                
                if produto and validade:
                    self.produtos.append((produto, validade))
                    # Adiciona na interface
                    produto_label = Label(
                        text=f"{produto} - {validade}",
                        size_hint_y=None,
                        height=40
                    )
                    self.produtos_layout.add_widget(produto_label)
                    
        except Exception as e:
            self.show_popup("Erro", f"Falha ao carregar produtos: {str(e)}")
    
    def adicionar_produto(self, instance):
        produto = self.produto_input.text.strip()
        validade = self.validade_input.text.strip()
        
        if produto and validade:
            try:
                # Valida a data
                datetime.datetime.strptime(validade, "%d/%m/%Y")
                
                # Adiciona localmente
                self.produtos.append((produto, validade))
                
                # Adiciona na interface
                produto_label = Label(
                    text=f"{produto} - {validade}",
                    size_hint_y=None,
                    height=30
                )
                self.produtos_layout.add_widget(produto_label)
                
                # Salva no Firestore
                self.salvar_no_firebase(produto, validade)
                
                # Limpa os campos
                self.produto_input.text = ""
                self.validade_input.text = ""
                
            except ValueError:
                self.show_popup("Erro", "Formato de data inválido. Use dd/mm/aaaa.")
        else:
            self.show_popup("Erro", "Preencha ambos os campos.")
    
    def salvar_no_firebase(self, produto, validade):
        try:
            db.collection('produtos').add({
                'nome': produto,
                'validade': validade,
                'data_adicao': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            self.show_popup("Erro", f"Falha ao salvar no Firebase: {str(e)}")
    
    def verificar_produtos(self, instance):
        hoje = datetime.datetime.today()
        for produto, validade in self.produtos:  # Indentação corrigida
            try:
                validade_data = datetime.datetime.strptime(validade, "%d/%m/%Y")
                dias_restantes = (validade_data - hoje).days
                
                if 61 <= dias_restantes <= 90:  # Alerta preventivo
                    notification.notify(
                        title=f"🔔 {produto} está chegando perto da validade",
                        message=f"Faltam {dias_restantes} dias (Vence em {validade})",
                        timeout=8
                    )
                elif 31 <= dias_restantes <= 60:  # Alerta médio
                    notification.notify(
                        title=f"⚠️ Atenção: {produto}",
                        message=f"Faltam {dias_restantes} dias para vencer!",
                        timeout=10
                    )
                elif 1 <= dias_restantes <= 30:  # Alerta urgente
                    notification.notify(
                        title=f"❗ URGENTE: {produto}",
                        message=f"VENCE EM {dias_restantes} DIAS! ({validade})",
                        timeout=15
                    )
                    
            except ValueError:
                pass
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.3))
        popup.open()

if __name__ == "__main__":
    ValidadeApp().run()