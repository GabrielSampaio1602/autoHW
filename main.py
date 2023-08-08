import os
from kaki.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.core.window import Window
from kivy.utils import platform
from kivy.config import Config
import trio
from kivy_widgets import color_definitions
from kivy_widgets.buttons import CButton
from kivy_widgets.icons import Icon
from kivy_widgets.dropdown import CDropDown

Config.set("kivy", "exit_on_escape", "0")

# Se aparecer a mensagem: '...não pode ser csock.connect((ip_address, port))arregado porque a execução de scripts foi desabilitada neste sistema.'
# --------------------------------------------------------------------------------------------------------------------
# https://vshare.com.br/error-execucao-de-scripts-foi-desabilitada-neste-sistema-powershell/
# Rodar no terminal PowerShell: Set-ExecutionPolicy -Scope CurrentUser
# E depois: RemoteSigned
# --------------------------------------------------------------------------------------------------------------------
# Na realidade ele está tentando buscar o python no seguinte caminho: C:\Users\gabri\.pyenv\pyenv-win\versions\3.10.9
# Mas esse caminho não ate, pois estou em outro computador
# O caminho correto é: C:\Users\ADM\.pyenv\pyenv-win\versions\3.10.9
# Ir em ".venv > pyenv.cfg" e colocar os caminhos corretos

# icons link: https://pictogrammers.com/library/mdi/

# buildozer -v android debug deploy run
# buildozer android logcat | grep python

# git pull <link>
# poetry shell
# Poetry install

# Se aparecer o problema: "import xxx could not be resolved"
# verificar se o python interpreter selecionado 'e o correto, referente ao virtual env certo
# Desinstalar e reinstalar a biblioteca em quest~ao


class MyScreenManager(F.ScreenManager):
    pass


class MainApp(App, MDApp):
    DEBUG = 1

    # Finding other .py folders
    PY_FOLDERS = []
    print(f'os.walk("screens") {os.walk("screens")}')
    for files in os.walk("screens"):
        for file in files[2]:
            if file.endswith(".py"):
                print(f"files[0] {files[0]}")
                py_path = os.path.join(os.getcwd(), files[0])
                print(f"py_path {py_path}")
                # py_path = py_path.replace('\\', '.')
                PY_FOLDERS.append(py_path)

    # Creating the list with the main.py file
    AUTORELOADER_PATHS = [(os.path.join(os.getcwd(), "main.py"), {"recursive": True})]

    # Adding other .py folders to the Autoreloader list
    for file in PY_FOLDERS:
        AUTORELOADER_PATHS.append((file, {"recursive": True}))

    print(f"AUTORELOADER_PATHS {AUTORELOADER_PATHS}")

    # Encontrando os arquivos KVs existentes na pasta Screen e nas pastas dentro dela
    #   e armazenando os caminhos nessa lista
    KV_FILES_LIST = []
    for files in os.walk("screens"):
        for file in files[2]:
            if file.endswith(".kv"):
                kv_path = os.path.join(os.getcwd(), os.path.join(files[0], file))
                KV_FILES_LIST.append(kv_path)
    print(f"KV_FILES {KV_FILES_LIST}")

    KV_FILES = set(KV_FILES_LIST)

    actual_screen = None

    def __init__(self, nursery):
        super().__init__()
        self.nursery = nursery

    def build_app(self):
        self.theme_cls.primary_palette = "Gray"
        self.screen_manager = MyScreenManager()

        # Load the last screen loaded, unless there isn't one, so load Main Screen
        if self.actual_screen == None:
            # screen = "Logs Screen"
            screen = "Main Screen"
            self.change_screen(screen)
            self.actual_screen = screen
        else:
            self.change_screen(self.actual_screen)

        if platform == "macosx":
            Window._set_window_pos(3540, 100)
            Window.size = (1312 * 0.2756777, 2460 * 0.296777)
        elif platform in ["linux", "win"]:
            Window.size = (270, 580)

        return self.screen_manager

    def change_screen(self, screen_name, direction="left"):
        # print("Changing to screen:", screen_name, "\n\n")

        self.screen_manager.transition.direction = direction
        if screen_name not in self.screen_manager.screen_names:
            screen_object = self.get_screen_object_from_screen_name(screen_name)
            self.screen_manager.add_widget(screen_object)

        self.screen_manager.current = screen_name
        self.actual_screen = screen_name

    def get_screen_object_from_screen_name(self, screen_name):
        # Parsing module 'my_screen.py' and object 'MyScreen' from screen_name 'My Screen'
        screen_module_in_str = "_".join([i.lower() for i in screen_name.split()])
        screen_object_in_str = "".join(screen_name.split())

        # Finding the specific path to file to be imported
        print(f"screen_module_in_str {screen_module_in_str}")
        print(f"screen_object_in_str {screen_object_in_str}")
        for full_kv_path in self.KV_FILES_LIST:
            if f"{screen_module_in_str}." in full_kv_path:
                screen_pos = full_kv_path.find("screen")
                path_from_screen_2_file = full_kv_path[screen_pos + 8 : -3]
                print(platform)
                if platform == "win":
                    path_2_import = path_from_screen_2_file.replace("\\", ".")
                elif platform in ["macosx", "linux"]:
                    path_2_import = path_from_screen_2_file.replace("/", ".")
                else:
                    path_2_import = path_from_screen_2_file.replace("\\", ".").replace(
                        "/", "."
                    )
                print(f"path_from_screen_2_file {path_from_screen_2_file}")
                print(f"path_2_import {path_2_import}")
                screen_module_in_str = path_2_import.replace("..", ".")

        # Importing screen object
        exec(f"from screens.{screen_module_in_str} import {screen_object_in_str}")

        # Instantiating the object
        screen_object = eval(f"{screen_object_in_str}()")

        return screen_object


if __name__ == "__main__":
    # Start kivy app as an asynchronous task
    async def main():
        async with trio.open_nursery() as nursery:
            await MainApp(nursery).async_run("trio")  # start Kivy
            nursery.cancel_scope.cancel()

    trio.run(main)
