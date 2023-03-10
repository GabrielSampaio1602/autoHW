from utils import load_kv_path
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

paths_folder = os.path.dirname(__file__)
inicio_screens = paths_folder.find("screens")
path_screen_2_file = paths_folder[inicio_screens:]
# print(path_screen_2_file)

name_file = os.path.basename(__file__)[:-3]
# print(name_file)
# print(f"{path_screen_2_file}\\{name_file}.kv")
# print(os.path.exists(f"{path_screen_2_file}/{name_file}.kv"))
load_kv_path(f"{path_screen_2_file}/{name_file}.kv")


class MainScreen(F.MDScreen):
    lista_contas = ListProperty(["GaloDoido", "Lars", "CrazyRooster"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.openedpopup = False

    def show_accs(self, *args, **kwargs):
        if self.openedpopup == False:
            self.bl_1 = MDCard(
                id="accs_bl",
                md_bg_color=[0, 0, 0, 0.7],
                orientation="vertical",
                pos_hint={"center_x": 0.5, "top": 0.52},
                size_hint_x=0.8,
                size_hint_y=0.21,
            )
            scroll_accounts = ScrollView(
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                size_hint_y=0.4,
            )
            self.accounts_bl = MDBoxLayout(
                orientation="vertical",
                spacing=2,
                padding=5,
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
            scroll_accounts.add_widget(self.accounts_bl)
            self.bl_1.add_widget(scroll_accounts)

            self.ids.mainfloat.add_widget(self.bl_1)
            self.openedpopup = True

    def select_acc(self, text, *args):
        self.ids.accounts_btn.text = str(text)
        # self.ids.accounts_btn.bind(text=self.update_text)
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
        # print(f"height {height}")
        self.accounts_bl.height = height
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


# ValueError: source code string cannot contain null bytes
# Havia uma linha aqui cheia de caracteres nulos (null) que estava fazendo o programa dar o erro acima
