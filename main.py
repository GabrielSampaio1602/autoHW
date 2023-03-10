import os
from kaki.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.core.window import Window
from kivy.utils import platform


class MyScreenManager(F.ScreenManager):
    pass


class MainApp(App, MDApp):
    DEBUG = 1

    # INÍCIO: CÓDIGOS ORIGINAIS
    # AUTORELOADER_PATHS = [
    #     (os.path.join(os.getcwd(), "main.py"), {"recursive": True}),
    #     (os.path.join(os.getcwd(), "screens"), {"recursive": True}),
    # ]
    #
    # KV_FILES = {
    #     os.path.join(os.getcwd(), f"screens/{screen_name}")
    #     for screen_name in os.listdir("screens")
    #     if screen_name.endswith(".kv")
    # }
    # FIM: CÓDIGOS ORIGINAIS

    # GABRIEL: INÍCIO DE ADAPTAÇÃO
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
    # GABRIEL: FIM DE ADAPTAÇÃO

    actual_screen = None

    def build_app(self):
        self.theme_cls.primary_palette = "Gray"
        self.screen_manager = MyScreenManager()

        # Load the last screen loaded, unless there isn't one, so load Main Screen
        if self.actual_screen == None:
            screen = "Logs Screen"
            self.change_screen(screen)
            self.actual_screen = screen
        else:
            self.change_screen(self.actual_screen)

        if platform == "macosx":
            Window._set_window_pos(3540, 100)
            Window.size = (1312 * 0.2756777, 2460 * 0.296777)
        else:
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

        # GABRIEL: INÍCIO DE ADAPTAÇÃO
        # Finding the specific path to file to be imported
        print(f"screen_module_in_str {screen_module_in_str}")
        print(f"screen_object_in_str {screen_object_in_str}")
        for full_kv_path in self.KV_FILES_LIST:
            if f"{screen_module_in_str}." in full_kv_path:
                screen_pos = full_kv_path.find("screen")
                path_from_screen_2_file = full_kv_path[screen_pos + 8 : -3]
                if platform == "windows":
                    path_2_import = path_from_screen_2_file.replace("\\", ".")
                elif platform in ["macosx", "linux"]:
                    path_2_import = path_from_screen_2_file.replace("/", ".")

                print(path_2_import)
                screen_module_in_str = path_2_import
        # print(f'screen_name {screen_name}')
        # print(f'screen_module_in_str {screen_module_in_str}')
        # GABRIEL: FIM DE ADAPTAÇÃO

        # Importing screen object
        # print(f'screen_module_in_str {screen_module_in_str}')
        # print(f'screen_object_in_str {screen_object_in_str}')
        exec(f"from screens.{screen_module_in_str} import {screen_object_in_str}")

        # Instantiating the object
        screen_object = eval(f"{screen_object_in_str}()")

        return screen_object


if __name__ == "__main__":
    MainApp().run()
