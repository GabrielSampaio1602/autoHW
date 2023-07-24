from utils import load_kv_path, contact_server
from kivy.factory import Factory as F
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.app import App
import os
from HWAppTrigger import send_command
import requests  # add to buildozer.spec/requests: openssl,hostpython3,urllib3, chardet,certifi,idna and enable INTERNET on Permissions
from sensitive_values import BDLINK
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.config import Config

Config.set("kivy", "exit_on_escape", "0")  # Talvez desnecess'ario
os.environ["KIVY_EXIT_ON_ESCAPE"] = "0"  # Talvez desnecess'ario


paths_folder = os.path.dirname(__file__)
inicio_screens = paths_folder.find("screens")
path_screen_2_file = paths_folder[inicio_screens:]
# print(path_screen_2_file)

name_file = os.path.basename(__file__)[:-3]
# print(name_file)
# print(f"{path_screen_2_file}\\{name_file}.kv")
# print(os.path.exists(f"{path_screen_2_file}/{name_file}.kv"))
load_kv_path(f"{path_screen_2_file}/{name_file}.kv".replace("..", "."))


class MainScreen(F.MDScreen):
    lista_contas = ListProperty(["GaloDoido", "Lars", "CrazyRooster"])
    running_to = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.openedpopup = False
        # Window.bind(on_keyboard=self.key_input)  # Vinculando açao ao teclado
        self.app = App.get_running_app()

    def on_enter(self):
        Clock.schedule_once(self.check_automation)
        Clock.schedule_interval(self.check_automation, 5)
        # win_height = Window.size[1]
        # print(f"win_height {win_height}")
        # self.ids.title_label.font_size = int(25 * win_height / 580)
        # self.ids.title_label.text = str(win_height)

        from kivy.base import EventLoop

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *args):
        # print(key)
        # print(window)
        # C'odigo comentado abaixo n~ao funcionou
        # if (
        #     key in [27, 1001] and self.app.screen_manager.current == "Main Screen"
        # ):  # 27 = ESC # 1001 = BACK_ANDROID
        #     self.app = App.get_running_app()
        #     previous_screen = self.app.screen_manager.previous()
        #     print(previous_screen)  # >> Main Screen
        #     self.app.change_screen(previous_screen, "right")
        #     return True  # Overwrite the default behavior (default: close window)
        if key in [27, 1001] and self.app.screen_manager.current == "Main Screen":
            self.app = App.get_running_app()
            # print(self.app.screen_manager.current)
            if self.app.screen_manager.current == "Main Screen":
                self.dialog = MDDialog(
                    text="Do you wanna quit?",
                    buttons=[
                        F.MDFlatButton(text="No", on_release=self.dismiss_popup),
                        F.MDFlatButton(text="Yes", on_release=self.app.stop),
                    ],
                )
                self.dialog.open()
            return True

    # Definindo aç~ao ao apertar o ESC/BACK
    def key_input(self, window, key, scancode, codepoint, modifier):
        if key in [27, 1001]:
            self.app = App.get_running_app()
            # print(self.app.screen_manager.current)
            if self.app.screen_manager.current == "Main Screen":
                self.dialog = MDDialog(
                    text="Do you wanna quit?",
                    buttons=[
                        F.MDFlatButton(text="No", on_release=self.dismiss_popup),
                        F.MDFlatButton(text="Yes", on_release=self.app.stop),
                    ],
                )
                self.dialog.open()

    def dismiss_popup(self):
        self.dialog.dismiss()

    def popup_server_off(self):
        self.dialog = F.MDDialog(
            text=f"The server is offline or isn't ready yet. Please try again in a few minutes or check if it's really on",
            buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
            anchor_x="center",
        )
        self.dialog.open()

    def show_accs(self, *args, **kwargs):
        if self.openedpopup == False:
            accs_btn_y = self.ids.accounts_btn.pos[1]
            accs_btn_h = self.ids.accounts_btn.size[1]
            # pos_bl_1 = int(accs_btn_y - accs_btn_h + 12)  # Ficou no meio do bot~ao
            # pos_bl_1 = int(accs_btn_y - accs_btn_h * 2)
            # O pos[1] retorna a altura do CENTRO do bot~ao, portanto SUBTRAIR a metade da altura dele (devemos subtrair pois no Kivy o 1 fica em cima e o 0 embaixo, ent~ao, se quisermos colocar um bot~ao abaixo do outro, ele deve ter um pos[1] menor que do botao referencia)
            # Ao pegar o POS, ele retorna o centro do Y
            # Ao posicionar pelo Y, ele tem como referencia o v'ertice inferior do wiget
            # Portanto, para posicionar abaixo do wiget de referencia temos que retirar 1 inteiro + metade dele (pois o POS esta no centro dele)
            pos_bl_1 = int(accs_btn_y - accs_btn_h * 3 / 2)

            print(f"accs_btn_y {accs_btn_y}")  # COMENTAR
            print(f"accs_btn_h {accs_btn_h}")  # COMENTAR
            print(f"pos_bl_1 {pos_bl_1}")  # COMENTAR
            self.bl_1 = MDCard(
                id="accs_bl",
                md_bg_color=[0, 0, 0, 0.7],
                orientation="vertical",
                # pos_hint={"center_x": 0.5, "top": 0.52},
                pos_hint={"center_x": 0.5},
                top=pos_bl_1,  # 270
                size_hint_x=0.8,
                # size_hint_y=0.21,
                size_hint_y=None,  # NOVO
            )
            scroll_accounts = ScrollView(
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                size_hint_y=0.4,
            )
            self.accounts_bl = MDBoxLayout(
                orientation="vertical",
                spacing=dp(5),
                padding=dp(5),
                size_hint_y=None,
                pos_hint={"center_x": 0.5},
                # definir height pela função vinculada pelo bind, após add os botões
            )

            # Acrescentando botões no self.accounts_bl
            btns_list = self.create_list_acc_btns(self.lista_contas)
            for btn, text in zip(btns_list, self.lista_contas):
                # Atribuindo o comando para o botão passando o text como parâmetro
                btn.on_release = lambda button_text=text: self.select_acc(button_text)
                # Adicionando o botão ao BoxLayout
                self.accounts_bl.add_widget(btn)

            self.accounts_bl.bind(minimum_height=self.update_height)

            self.bl_1.bind(minimum_height=self.setter("height"))  # FUNCIONA
            # self.bl_1.height = self.bl_1.minimum_height # FUNCIONA
            # self.accounts_bl.bind(minimum_height=self.setter("height"))  # FUNCIONA
            self.accounts_bl.height = self.bl_1.minimum_height  # FUNCIONA
            # self.bl_1.height = self.accounts_bl.height  # NOVO

            scroll_accounts.add_widget(self.accounts_bl)
            self.bl_1.add_widget(scroll_accounts)
            # scroll_accounts.height = self.bl_1.minimum_height  # FUNCIONA

            self.ids.mainfloat.add_widget(self.bl_1)
            self.openedpopup = True

    def select_acc(self, text, *args):
        self.ids.accounts_btn.text = str(text)
        print("bl_1 pos_y:", int(self.bl_1.pos[1]))  # COMENTAR
        self.ids.mainfloat.remove_widget(self.bl_1)
        self.openedpopup = False

    def create_list_acc_btns(self, list_accounts, *args, **kwargs):
        btns_list = []
        for i, acc in enumerate(list_accounts):
            setattr(
                self,
                f"acc_btn{i}",
                MDRaisedButton(
                    id=f"{acc}",
                    text=f"{acc}",
                    text_color=[0, 0, 0, 0.7],
                    size_hint_x=0.95,
                    md_bg_color=[0.8, 0.8, 0.8, 1],
                    pos_hint={"center_x": 0.5},
                ),
            )  # Deixar sem o comando por enquanto, acrescentar
            # quando acrescentá-los ao container
            btns_list.append(getattr(self, f"acc_btn{i}"))
        return btns_list

    def update_height(self, instance, *args):
        # Get the actual height of the BoxLayout after it is drawn
        height = instance.minimum_height
        self.accounts_bl.height = height
        self.bl_1.height = height  # NOVO
        return height

    def show_warning_popup(self, message):
        popup_btn = MDRaisedButton(
            text="OK",
            on_release=lambda *args: popup.dismiss(),
            pos_hint={"center_x": 0.5},
        )
        popup = MDDialog(
            title="Wait!",
            text=message,
            # radius=[20, 7, 20, 7],
            size_hint=[0.8, None],
            buttons=[popup_btn],
        )
        popup.open()

    def go_to_logs(self):
        if self.ids.accounts_btn.text not in self.lista_contas:
            self.show_warning_popup("Select an account to Show the Logs!")
        else:
            app = App.get_running_app()
            app.change_screen("Logs Screen", "left")
            # Para acessar objetos de outras telas, usar o root.manager.get_screen()
            # Ex: reference_to_next_screen = self.manager.get_screen("home_screen")
            #     reference_to_next_screen.ids.text_input.text = "new text"

    def go_to_automation(self):
        # if self.ids.accounts_btn.text not in self.lista_contas:
        #     self.show_warning_popup("Select an account to run the automation!")
        # else:
        app = App.get_running_app()
        app.change_screen("Automation Screen", "left")
        # Para acessar objetos de outras telas, usar o root.manager.get_screen()
        # Ex: reference_to_next_screen = self.manager.get_screen("home_screen")
        #     reference_to_next_screen.ids.text_input.text = "new text"

    def hibernar_pc(self, comando=""):
        # print(comando)
        # if comando not in ["Hibernar", "Iniciar"]:
        #     açao = "Comando inesperado"
        #     print(açao)
        #     return açao
        # result, message = send_command(comando) # ANTIGO, VIA SOCKET
        req = contact_server("hibernar", self.popup_server_off)
        result, message = req, req.text
        print(result, message)
        self.dialog = F.MDDialog(
            text=message,
            buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
        )
        self.dialog.open()

    def dismiss_popup(self, popup):
        self.dialog.dismiss()

    def check_automation(self, dt):
        # win_height = Window.size[1]
        # print(f"win_height {win_height}")
        # self.ids.title_label.font_size = int(25 * win_height / 580)
        # self.ids.title_label.text = str(win_height)

        running_to_update = requests.get(f"{BDLINK}/Running_Info/.json").json()[
            "running_to"
        ]
        if running_to_update != self.running_to:
            self.mainscreen = App.get_running_app().screen_manager.get_screen(
                "Main Screen"
            )
            self.mainscreen.ids.running_label.text = (
                f"Currently running automation to\n{running_to_update}"
            )
            # if running_to_update == "None":
            #     self.mainscreen.ids.running_label.text_color = [0, 0, 0, 0.5]
            # else:
            #     self.mainscreen.ids.running_label.text_color = [0.1, 0.7, 0.1, 1]
            self.mainscreen.ids.running_label.text_color = (
                [0, 0, 0, 0.3] if running_to_update == "None" else [0.1, 0.7, 0.1, 0.7]
            )
            self.running_to = running_to_update


# ValueError: source code string cannot contain null bytes
# Havia uma linha aqui cheia de caracteres nulos (null) que estava fazendo o programa dar o erro acima
