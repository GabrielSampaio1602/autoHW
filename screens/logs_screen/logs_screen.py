from utils import load_kv_path
from kivy.factory import Factory as F
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import sp, dp
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.pickers import MDDatePicker
import os
import requests
from datetime import datetime
from sensitive_values import BDLINK, MAC, IP, EXE_PATH
from wakeonlan import send_magic_packet
from kivy.config import Config
import trio
from datetime import datetime
import time
import multiprocessing
import threading

Config.set("kivy", "exit_on_escape", "0")  # Talvez desnecess'ario
os.environ["KIVY_EXIT_ON_ESCAPE"] = "0"  # Talvez desnecess'ario

# icons link: https://pictogrammers.com/library/mdi/

paths_folder = os.path.dirname(__file__)
inicio_screens = paths_folder.find("screens")
path_screen_2_file = paths_folder[inicio_screens:]

name_file = os.path.basename(__file__)[:-3]
# load_kv_path(f"{path_screen_2_file}/{name_file}.kv") # Comentado pois estava duplicando os botões no widget logs_box

padding = 10


class CustomButton(RectangularRippleBehavior, F.ButtonBehavior, F.BoxLayout):
    text = F.StringProperty("Botão")
    tamanho_da_fonte = F.NumericProperty(sp(18))
    icon = F.StringProperty("")
    cor_do_fundo = F.ColorProperty([1, 1, 1, 1])
    cor_da_fonte = F.ColorProperty([0, 0, 0, 1])
    cor_do_icone = F.ColorProperty([0, 0, 0, 1])
    raio_da_borda = F.ListProperty([dp(5)])


class SmartRV(F.RecycleView):
    """
    This RecycleView implements a smart scroll behavior.
    You can select the item you want to scroll to by using the
    function to scroll to an item called `scroll_to_item`. You will
    be able to scroll to the item by using the item's index, and you can
    select among three different scroll behaviors: `scroll_to_top`,
    `scroll_to_center` and `scroll_to_bottom`.
    """

    orientation = F.OptionProperty("vertical", options=["vertical", "horizontal"])

    children_height = F.NumericProperty()
    children_width = F.NumericProperty()

    vertical_behavior = F.OptionProperty(
        "scroll_to_top",
        options=["scroll_to_top", "scroll_to_center", "scroll_to_bottom"],
    )
    horizontal_behavior = F.OptionProperty(
        "scroll_to_left",
        options=["scroll_to_left", "scroll_to_center", "scroll_to_right"],
    )
    scroll_duration = F.NumericProperty(1)

    def scroll_to_item(self, index):
        """
        Scroll to the item at the given index.
        :param index: The index of the item to scroll to.
        """
        if not self.data:
            return

        if self.orientation == "vertical":
            N = len(self.data)  # number of items

            h = self.children_height  # height of each item
            H = self.height  # height of the RecycleView

            if self.vertical_behavior == "scroll_to_top":
                scroll_y = 1 - (index * h) / (N * h - H)
            elif self.vertical_behavior == "scroll_to_center":
                scroll_y = 1 - (index * h - H / 2 + h / 2) / (N * h - H)
            elif self.vertical_behavior == "scroll_to_bottom":
                scroll_y = 1 - (index * h - H + h) / (N * h - H)

            Animation(scroll_y=scroll_y, d=self.scroll_duration).start(self)

        elif self.orientation == "horizontal":
            N = len(self.data)  # number of items

            w = self.children_width  # width of each item
            W = self.width  # width of the RecycleView

            if self.horizontal_behavior == "scroll_to_left":
                scroll_x = (index * w) / (N * w - W)

            elif self.horizontal_behavior == "scroll_to_center":
                scroll_x = (index * w - W / 2 + 1 / 2 * w) / (N * w - W)

            elif self.horizontal_behavior == "scroll_to_right":
                scroll_x = (index * w - W + w) / (N * w - W)

            Animation(scroll_x=scroll_x, d=self.scroll_duration).start(self)


class Log(F.MDBoxLayout):
    def __init__(self, log_text="", log_class="", **kwargs):
        super().__init__(**kwargs)
        self.ids.log_btn.text = log_text
        self.app = App.get_running_app()

        # Agendar para obter extrair a largura após o botão estar alterado
        Clock.schedule_once(self.get_button_width)

    def get_button_width(self, *args):
        button = self.ids.log_btn
        button.ref_texture = True
        button_width = button.width
        # # Essa função, agendada pelo Clock, printa a largura do log após ser renderizado
        # print(f"Button width: {button_width}")
        LogsScreen.widths.append(button_width)

        # print(LogsScreen.widths)
        # print(max(LogsScreen.widths))

        # Definir a maior largura e margens
        maior_largura = max(LogsScreen.widths)
        margens = padding * 2

        # Atribuir a soma desses valores à largura do BoxLayout (logs_box)
        logscreen = self.app.screen_manager.get_screen("Logs Screen")
        logscreen.ids.logs_box.width = maior_largura + margens


class FiltersSelection(F.MDGridLayout):
    pass


class DateBoxLayout(F.BoxLayout):
    pass


class Filter(RectangularRippleBehavior, F.ButtonBehavior, F.BoxLayout):
    text = F.StringProperty("Botão")
    tamanho_da_fonte = F.NumericProperty(sp(18))
    icon = F.StringProperty("")
    cor_do_fundo = F.ColorProperty([1, 1, 1, 1])
    cor_da_fonte = F.ColorProperty([0, 0, 0, 1])
    cor_do_icone = F.ColorProperty([0, 0, 0, 1])
    raio_da_borda = F.ListProperty([dp(5)])


class CalendarButton(RectangularRippleBehavior, F.ButtonBehavior, F.FloatLayout):
    text = F.StringProperty("")
    text_day = F.StringProperty("")
    text_month = F.StringProperty("")
    tamanho_da_fonte = F.NumericProperty(sp(18))
    icon = F.StringProperty("")
    cor_do_fundo = F.ColorProperty([1, 1, 1, 1])
    cor_da_fonte = F.ColorProperty([0, 0, 0, 1])
    cor_do_icone = F.ColorProperty([0, 0, 0, 1])
    raio_da_borda = F.ListProperty([dp(5)])


class GoTopButton(RectangularRippleBehavior, F.ButtonBehavior, F.FloatLayout):
    text = F.StringProperty("")
    text_day = F.StringProperty("")
    text_month = F.StringProperty("")
    tamanho_da_fonte = F.NumericProperty(sp(18))
    icon = F.StringProperty("")
    cor_do_fundo = F.ColorProperty([1, 1, 1, 1])
    cor_da_fonte = F.ColorProperty([0, 0, 0, 1])
    cor_do_icone = F.ColorProperty([0, 0, 0, 1])
    raio_da_borda = F.ListProperty([dp(90)])


class LoadingPopup(F.BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self.open_nurseries)
        self.angle = self.ids.loading_icon.angle
        self.begin = datetime.now()

    def open_nurseries(self, *args):
        self.app.nursery.start_soon(self.animate_loading)
        self.app.nursery.start_soon(self.update_elapsed)

    def start_animate_loading(self, *args):
        self.app.nursery.start_soon(self.animate_loading)

    async def animate_loading(self, *args):
        self.angle -= (
            360 * 100
        )  # Aumentando a duraç~ao da animaç~ao para n~ao ter que ficar se preocupando com ela o tempo todo
        duration = 0.5 * 100
        animation = Animation(angle=self.angle, duration=duration)
        animation.bind(on_complete=self.start_animate_loading)
        animation.start(self.ids.loading_icon)
        await trio.sleep(0.01)

    def start_update_elapsed(self, *args):
        self.app.nursery.start_soon(self.update_elapsed)

    async def update_elapsed(self, *args):
        elapsed = str(datetime.now() - self.begin)[2:11]
        self.ids.loading_label.text = f"Time elapsed: {elapsed}"
        self.start_update_elapsed()


class LogsScreen(F.MDScreen):
    # Definindo lista com as larguras de todos os botões criados
    widths = []
    title = F.StringProperty()
    auto_scroll_on = F.BooleanProperty(True)
    i = 0
    is_filters_screen_opened = F.BooleanProperty(False)
    actual_filter = F.StringProperty()
    angle = F.NumericProperty(0)

    data = F.DictProperty()

    last_logs = F.DictProperty()

    current_logs = F.ListProperty()

    account = F.StringProperty()  # "GaloDoido"

    date = F.StringProperty()  # "12-05-23"

    BD_LINK = BDLINK

    actual_filter = F.StringProperty("All")

    year = datetime.now().strftime("%Y")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.loading_popup = None

    def on_enter(self):
        self.data = {
            "HerosWay": [
                "highway",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Loja": [
                "store-outline",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Outland": [
                "rhombus",  # cards-diamong
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "MissionsTab": [
                "clipboard-check-outline",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Tower": [
                "chess-rook",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "DailyQuests": [
                "notebook",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Mail": [
                "email-seal-outline",  # email-outline
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Airship": [
                "airballoon-outline",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "HeroicChest": [
                "treasure-chest",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Exchange": [
                "bitcoin",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Boxy": [
                "gift-outline",
                "on_release",
                lambda x: x.parent.parent.call(x),
            ],
            "Theater": [
                "ticket-outline",
                "on_release",
                lambda x: self.call(x),
            ],
            "SystemLogs": [
                "math-log",
                "on_release",
                lambda x: self.call(x),
            ],
            "All": [
                "expand-all-outline",  # select-all
                "on_release",
                lambda x: self.call(x),
            ],
        }

        self.actual_filter = "All"
        Clock.schedule_once(self.assign_function)
        # Clock.schedule_once(self.update_all_logs, 5)

        # call update_current_logs every 60 seconds
        Clock.schedule_interval(self.update_current_logs, 60)
        Clock.schedule_once(self.assign_day_month)

        from kivy.base import EventLoop

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        Clock.schedule_once(self.update_all_logs)

    def hook_keyboard(self, window, key, *args):
        # print(key)
        # print(window)
        if (
            key in [27, 1001] and self.app.screen_manager.current == "Logs Screen"
        ):  # 27 = ESC # 1001 = BACK_ANDROID
            # self.app = App.get_running_app()
            previous_screen = self.app.screen_manager.previous()
            print(previous_screen)  # >> Main Screen
            self.app.change_screen(previous_screen, "right")
            return True  # Overwrite the default behavior (default: close window)

    def assign_day_month(self, dt):
        self.logscreen.ids.calendar_button_new.text_day = datetime.now().strftime("%d")
        self.logscreen.ids.calendar_button_new.text_month = datetime.now().strftime(
            "%m"
        )

    def open_calendar(self):
        results = requests.get(f"{self.BD_LINK}/Logs/.json").json()
        logs_dates = [
            datetime.strptime(date, "%d-%m-%y") for date in list(results.keys())
        ]
        min_date = min(logs_dates).date()
        max_date = max(logs_dates).date()

        date_dialog = MDDatePicker(
            year=int(self.year),
            month=int(self.logscreen.ids.calendar_button_new.text_month),
            day=int(self.logscreen.ids.calendar_button_new.text_day),
            min_date=min_date,
            max_date=max_date,
        )

        # Talvez ficará ok no celular sem precisar ajustar aqui
        # date_dialog.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        # date_dialog.size_hint = (0.8, 0.8)
        # print(date_dialog.pos_hint)

        date_dialog.bind(on_save=self.get_new_date)
        date_dialog.open()

    def go_to_top(self):
        scrollview = self.app.screen_manager.get_screen("Logs Screen").ids.scrollview
        scrollview.scroll_y = 1

    def go_to_bottom(self):
        scrollview = self.app.screen_manager.get_screen("Logs Screen").ids.scrollview
        scrollview.scroll_y = 0

    def get_new_date(self, instance, value, date_range):
        # print(f"value {value}")
        # day = datetime.strptime(value, "%d %B, %Y")
        # month = datetime.strptime(value, "%d %B, %Y")

        date = datetime.strftime(value, "%d-%m-%y")
        selected_date = datetime.strptime(date, "%d-%m-%y")
        if selected_date <= datetime.now():
            day = datetime.strftime(value, "%d")
            self.logscreen.ids.calendar_button_new.text_day = day

            month = datetime.strftime(value, "%m")
            self.logscreen.ids.calendar_button_new.text_month = month

            self.year = datetime.strftime(value, "%Y")
            self.date = date

            self.app.nursery.start_soon(self.update_all_logs)
        else:
            self.open_calendar()

    def change_pause_color(self, dt):
        # self.data = {}
        logscreen = self.app.screen_manager.get_screen("Logs Screen")
        pause = logscreen.ids.topbar.right_action_items
        print("oi")
        print(type(pause))
        eval(f"({pause[0][1]})()")

    # Ajustar
    def get_account_name(self):
        try:
            # self.app = App.get_running_app()
            mainscreen = self.app.screen_manager.get_screen("Main Screen")
            btn = mainscreen.ids.accounts_btn
            text = btn.text
            return text
        except:
            return "GaloDoido"

    def get_and_organize_logs_old(self):  # , account, date, BD_LINK
        logs = requests.get(
            f"{self.BD_LINK}/Logs/{self.date}/{self.account}/.json"
        ).json()

        # md-icon and color
        groups = [
            "HerosWay",
            "Loja",
            "Outland",
            "MissionsTab",
            "Tower",
            "DailyQuests",
            "Mail",
            "Airship",
            "HeroicChest",
            "Exchange",
            "Boxy",
            "Theater",
            "SystemLogs",
            "All",
        ]

        # Dynamically creating a list for each group
        for group in groups:
            setattr(self, group, list())

        # Append each log for All and for its the respective group
        for log in logs:
            horário = list(logs[log].keys())[0]
            ação = list(logs[log].values())[0]
            log = f"[{horário}] {ação}"

            self.All.append(log)

            # Appending each log for its respective group
            syslog = True
            for group in groups:
                if (
                    group.lower() in ação.replace("'", "").replace(" ", "").lower()
                    and group != "All"
                ):
                    getattr(self, group).append(log)
                    syslog = False

            # If the log didn't fit in the other groups, put it in the SystemLogs
            if syslog == True:
                getattr(self, "SystemLogs").append(log)

        # Creating a dict with [key = group] and [value = group's list]
        groups_dict = dict()
        for group in groups:
            groups_dict[group] = getattr(self, group)

        # for group in groups:
        #     if "Boxy" in group and group != "Boxy":
        #         print(group)

        return groups_dict

    # EXCLUIR
    def add_log_old(self):
        logscreen = self.app.screen_manager.get_screen("Logs Screen")

        if self.i == 0:
            logscreen = self.app.screen_manager.get_screen("Logs Screen")
            logscreen.ids.logs_box.clear_widgets()
        logs_box = self.ids.logs_box
        log = Log(
            f"botão oooooooooooooooooooo {self.i}",
            "Loja",
        )
        self.i += 1
        logs_box.add_widget(log)

        logs_box.bind(minimum_height=self.update_height)

        scrollview = logscreen.ids.scrollview
        # Se [altura atual] + [altura botão] > [altura do scrollview]
        is_time_to_scroll = logs_box.height + log.height > scrollview.height

        if is_time_to_scroll and self.auto_scroll_on:
            scrollview.scroll_y = 0
        elif is_time_to_scroll and self.auto_scroll_on == False:
            # altura = log.height
            # dist_mantain_position = scrollview.convert_distance_to_scroll(0, altura)[1]
            # y_final = dist_mantain_position * altura
            # scrollview.scroll_y = y_final
            # print(f"altura {y_final}")
            altura = log.height
            tamanho_scroll = logscreen.ids.logs_box.height
            old_pos = ((scrollview.scroll_y * tamanho_scroll) + altura) / (
                tamanho_scroll + altura
            )
            scrollview.scroll_y = old_pos

            # teste
            # scrollview.do_scroll_y = False
            # teste

        """altura = log.height
        tamanho_scroll = logscreen.ids.logs_box.height
        dist_prop_após_add = altura / (tamanho_scroll)
        dist_relativ_após_add = (dist_prop_após_add) * (1 - scrollview.scroll_y)
        # new_pos = scrollview.scroll_y - dist_prop_após_add
        print(f"tamanho_scroll {tamanho_scroll}")
        print(f"dist_relativ_após_add {dist_relativ_após_add}")
        print(f"scrollview.scroll_y {scrollview.scroll_y}")
        # scrollview.scroll_y += dist_prop_após_add
        old_pos = ((scrollview.scroll_y * tamanho_scroll) + altura) / (
            tamanho_scroll + altura
        )  # * (1 - dist_relativ_após_add)
        scrollview.scroll_y = old_pos"""
        # scrollview.scroll_y *= 1 - dist_relativ_após_add

        # # Essa função printa a largura do log antes de renderizá-lo
        # print(f"log.width {log.width}")

        # print(f"log.get_button_width() {log.get_button_width()}")
        # print(logscreen.ids.log)

    # EXCLUIR
    def add_log(self, log_text, log_class):
        logscreen = self.app.screen_manager.get_screen("Logs Screen")

        if self.i == 0:
            logscreen = self.app.screen_manager.get_screen("Logs Screen")
            logscreen.ids.logs_box.clear_widgets()
        logs_box = self.ids.logs_box
        log = Log(
            log_text,
            log_class,
        )
        self.i += 1
        logs_box.add_widget(log)

        logs_box.bind(minimum_height=self.update_height)

        scrollview = logscreen.ids.scrollview
        is_time_to_scroll = logs_box.height + log.height > scrollview.height

        if is_time_to_scroll and self.auto_scroll_on:
            scrollview.scroll_y = 0
        elif is_time_to_scroll and self.auto_scroll_on == False:
            altura = log.height
            tamanho_scroll = logscreen.ids.logs_box.height
            old_pos = ((scrollview.scroll_y * tamanho_scroll) + altura) / (
                tamanho_scroll + altura
            )
            scrollview.scroll_y = old_pos

    def async_add_log(self, log_text, log_class):
        logscreen = self.app.screen_manager.get_screen("Logs Screen")

        if self.i == 0:
            logscreen = self.app.screen_manager.get_screen("Logs Screen")
            logscreen.ids.logs_box.clear_widgets()
        logs_box = self.ids.logs_box
        log = Log(
            log_text,
            log_class,
        )
        self.i += 1
        logs_box.add_widget(log)

        logs_box.bind(minimum_height=self.update_height)

        scrollview = logscreen.ids.scrollview
        is_time_to_scroll = logs_box.height + log.height > scrollview.height

        if is_time_to_scroll and self.auto_scroll_on:
            scrollview.scroll_y = 0
        elif is_time_to_scroll and self.auto_scroll_on == False:
            altura = log.height
            tamanho_scroll = logscreen.ids.logs_box.height
            old_pos = ((scrollview.scroll_y * tamanho_scroll) + altura) / (
                tamanho_scroll + altura
            )
            scrollview.scroll_y = old_pos

    async def open_loading_popup(self, *args):
        self.angle = 0
        self.loading_popup = LoadingPopup()
        self.add_widget(self.loading_popup)
        # print(dir(App.get_running_app().root))
        # App.get_running_app().root.ids.float_layout.add_widget(self.loading_popup)
        # self.icon = self.loading_popup.ids.loading_icon
        # await trio.sleep(0.001) # Fundamental to give time to the other coroutine to run "simultaneously"

    # EXCLUIR
    def process_open_loading_popup(self, *args):
        self.loading_popup = LoadingPopup()
        self.add_widget(self.loading_popup)
        # self.icon = self.loading_popup.ids.loading_icon
        # await trio.sleep(0.001) # Fundamental to give time to the other coroutine to run "simultaneously"

    def close_loading_popup(self, *args):
        self.remove_widget(self.loading_popup)
        self.loading_popup = None

    def update_all_logs(self, dt=0):
        self.angle = 0

        # trio
        self.app.nursery.start_soon(self.open_loading_popup)

        # # multiprocessing
        # queue = multiprocessing.Queue()
        # self.loading_popup_process = multiprocessing.Process(
        #     target=self.process_open_loading_popup
        # )
        # self.loading_popup_process.daemon = True
        # self.loading_popup_process.start()
        # self.loading_popup_process.join()

        # # threading - ERRO
        # thread = threading.Thread(target=self.process_open_loading_popup, daemon=True)
        # thread.start()

        print(datetime.now())
        self.app.nursery.start_soon(self.async_update_all_logs)  # RODAR ESSE
        # update_logs = multiprocessing.Process(target=self.process_update_all_logs)
        # update_logs.start()

    async def async_update_all_logs(self):
        print(f"Updating logs to {self.account} on {self.date}")
        await trio.sleep(
            1
        )  # Fundamental to give time to the loading coroutine to start first
        dict_all_logs = self.get_and_organize_logs(self.get_new_logs())
        self.clear_logs_box_widget()
        if dict_all_logs == None:
            self.logscreen.ids.no_logs_label.text = "No logs found"
            return None
        print(f"before add_logs: {datetime.now()}")
        i = 0
        reset = datetime.now()
        # print(dict_all_logs[self.actual_filter])
        # print(len(dict_all_logs[self.actual_filter]))
        for value in dict_all_logs[self.actual_filter]:
            self.add_log(value, self.actual_filter)
            # await self.app.nursery.start_soon(self.async_add_log, value, self.actual_filter)
            self.current_logs.append(value)

            now = datetime.now()
            # converter de seconds para microseconds
            if (now - reset).microseconds >= 1000 * 0.5 * 100:
                await trio.sleep(0.5)
                reset = datetime.now()
                # print("aqui")  # 1.000.000
                # print(now)

            # i += 1
            # if i == 10:
            #     await trio.sleep(
            #         0.001
            #     )  # Fundamental to give time to the other coroutine to run "simultaneously"
            #     i = 0

        print(f"after add_logs: {datetime.now()}")
        self.logscreen.ids.no_logs_label.text = ""
        print(f"Updated! {datetime.now()}")
        # self.remove_widget(self.loading_popup)
        # self.loading_popup = None
        self.close_loading_popup()

    # EXCLUIR
    def process_update_all_logs(self):
        print(f"Updating logs to {self.account} on {self.date}")
        dict_all_logs = self.get_and_organize_logs(self.get_new_logs())
        self.clear_logs_box_widget()
        if dict_all_logs == None:
            self.logscreen.ids.no_logs_label.text = "No logs found"
            return None
        print(f"before add_logs: {datetime.now()}")
        i = 0
        for value in dict_all_logs[self.actual_filter]:
            self.add_log(value, self.actual_filter)
            self.current_logs.append(value)
        print(f"after add_logs: {datetime.now()}")
        self.logscreen.ids.no_logs_label.text = ""
        print(f"Updated! {datetime.now()}")
        # self.remove_widget(self.loading_popup)
        self.close_loading_popup()

    def update_current_logs(self, dt=0):
        # self.angle = 0
        # self.loading_popup = LoadingPopup()
        # self.add_widget(self.loading_popup)
        # self.icon = self.loading_popup.ids.loading_icon
        self.app.nursery.start_soon(self.open_loading_popup)
        self.app.nursery.start_soon(self.async_update_current_logs)
        print("Updating current logs")

    async def async_update_current_logs(self, dt=0):
        # print(self.loading_popup)
        while self.loading_popup == None:
            print('travado')
            await trio.sleep(
                0.1
            )  # Fundamental to give time to the loading coroutine to start first
        running_to_update = requests.get(f"{BDLINK}/Running_Info/.json").json()[
            "running_to"
        ]
        today = datetime.now().strftime("%d-%m-%y")
        if running_to_update != self.account or today != self.date:
            # self.remove_widget(self.loading_popup)
            # self.loading_popup = None
            self.close_loading_popup()
            return
        print(f"Updating logs to {self.account} on {self.date}")
        # time.sleep(5)
        print("Problema apos aqui")
        dict_all_logs = self.get_and_organize_logs(self.get_new_logs())
        if dict_all_logs == None:
            self.logscreen.ids.no_logs_label.text = "No logs found"
            # self.remove_widget(self.loading_popup)
            # self.loading_popup = None
            self.close_loading_popup()
            return None
        fresh_current_logs = dict_all_logs[self.actual_filter]
        for fresh_log in fresh_current_logs:
            if fresh_log not in self.current_logs:
                self.add_log(fresh_log, self.actual_filter)
                self.current_logs.append(fresh_log)

        self.logscreen.ids.no_logs_label.text = ""
        print("Updated!")
        # self.remove_widget(self.loading_popup)
        # self.loading_popup = None
        self.close_loading_popup()

    def update_height(self, instance, *args):
        # Get the actual height of the widget (BoxLayout) after it is redrawn
        height = instance.minimum_height
        return height

    def clear_logs_box_widget(self):
        logscreen = self.app.screen_manager.get_screen("Logs Screen")
        logscreen.ids.logs_box.clear_widgets()
        self.current_logs.clear()

    def go_back_to_main_screen(self):
        self.app.change_screen("Main Screen", "right")
        self.clear_logs_box_widget()

    def change_autoscroll(self, widget):
        print(widget)

        if widget.icon == "toggle-switch":
            widget.icon = "toggle-switch-off"
            widget.icon_color = [0.8, 0, 0, 1]
            self.auto_scroll_on = False
        elif widget.icon == "toggle-switch-off":
            widget.icon = "toggle-switch"
            widget.icon_color = [1, 1, 1, 1]  # [0, 0.7, 0, 1]
            self.auto_scroll_on = True
        elif widget.icon == "pause":
            widget.icon = "play"
            widget.icon_color = [0.8, 0, 0, 1]
            self.auto_scroll_on = False
        elif widget.icon == "play":
            widget.icon = "pause"
            widget.icon_color = [0, 1, 0, 1]  # [0, 0.7, 0, 1]
            self.auto_scroll_on = True

    def printar(self, text):
        logs_screen = self.app.screen_manager.get_screen("Logs Screen")
        print(text)
        # logs_screen.ids.floating_button.on_touch_down()

    def call(self, button):
        print("called from", button.icon)

        # Minimizar menu
        logs_screen = self.app.screen_manager.get_screen("Logs Screen")
        logs_screen.ids.floating_button.close_stack()

    def assign_function(self, dt):
        self.logscreen = self.app.screen_manager.get_screen("Logs Screen")
        self.logscreen.ids.filter_button.on_release = self.open_filters_screen

        self.account = self.get_account_name()
        self.date = datetime.now().strftime("%d-%m-%y")

    def open_filters_screen(self):
        if self.is_filters_screen_opened == False:
            self.filters_screen = FiltersSelection()

            for name in self.data:
                btn = Filter(
                    text=name,
                    icon=self.data[name][0],
                    on_release=self.select_filter,
                )
                # Creating the anchor layout to put and center the button
                anchor = F.AnchorLayout(anchor_x="center", anchor_y="center")
                anchor.add_widget(btn)
                self.filters_screen.add_widget(anchor)
                # print(self.data[name][0])

            self.ids.float_layout.add_widget(self.filters_screen)
            self.is_filters_screen_opened = True

            animation = Animation(angle=30, duration=0.1)
            animation.start(self.ids.filter_button)

            # print(self.logscreen.ids.float_layout.height)
            # print(self.logscreen.ids.float_layout.width)

    def select_filter(self, button):
        # print("Called from", button.text)
        previous_filter = self.actual_filter
        self.actual_filter = button.text

        float_layout = self.ids.float_layout
        float_layout.remove_widget(self.filters_screen)
        self.is_filters_screen_opened = False

        animation = Animation(angle=0, duration=0.1)
        animation.start(self.ids.filter_button)

        if button.text == "All":
            self.logscreen.ids.filter_button.icon = "filter"
            self.logscreen.ids.filter_button.cor_icone = [0, 0, 0, 1]
        else:
            self.logscreen.ids.filter_button.icon = button.icon
            self.logscreen.ids.filter_button.cor_icone = [0, 0, 0, 0.65]

        if previous_filter != self.actual_filter:
            self.update_all_logs()

    def get_new_logs(self):
        return requests.get(
            f"{self.BD_LINK}/Logs/{self.date}/{self.account}/.json"
        ).json()

    def compare_logs(self, added_logs, actual_logs):
        new_logs = dict()

        # Comparing actual logs to old ones to identify new ones
        for log in actual_logs:
            if log not in added_logs:
                new_logs[log] = actual_logs[log]

        return new_logs

    def get_and_organize_logs(self, logs):
        groups = [
            "HerosWay",
            "Loja",
            "Outland",
            "MissionsTab",
            "Tower",
            "DailyQuests",
            "Mail",
            "Airship",
            "HeroicChest",
            "Exchange",
            "Boxy",
            "Theater",
            "SystemLogs",
            "All",
        ]

        # Dynamically creating a list for each group
        for group in groups:
            setattr(self, group, list())
        if logs == None:
            return None
        # Append each log for All and for its the respective group
        for log in logs:
            horário = list(logs[log].keys())[0]
            ação = list(logs[log].values())[0]
            log = f"[{horário}] {ação}"

            self.All.append(log)

            # Appending each log for its respective group
            syslog = True
            for group in groups:
                if (
                    group.lower() in ação.replace("'", "").replace(" ", "").lower()
                    and group != "All"
                ):
                    getattr(self, group).append(log)
                    syslog = False

            # If the log didn't fit in the other groups, put it in the SystemLogs
            if syslog == True:
                getattr(self, "SystemLogs").append(log)

        # Creating a dict with [key = group] and [value = group's list]
        groups_dict = dict()
        for group in groups:
            groups_dict[group] = getattr(self, group)

        return groups_dict
