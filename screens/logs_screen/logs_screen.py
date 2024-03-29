import os
from datetime import datetime

import asks
import trio
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory as F
from kivy.metrics import dp, sp
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.pickers import MDDatePicker
from wakeonlan import send_magic_packet

from sensitive_values import BDLINK, EXE_PATH, IP, MAC
from utils import create_session, load_kv_path

Config.set("kivy", "exit_on_escape", "0")  # Talvez desnecess'ario
os.environ["KIVY_EXIT_ON_ESCAPE"] = "0"  # Talvez desnecess'ario

# icons link: https://pictogrammers.com/library/mdi/

paths_folder = os.path.dirname(__file__)
inicio_screens = paths_folder.find("screens")
path_screen_2_file = paths_folder[inicio_screens:]

name_file = os.path.basename(__file__)[:-3]
# load_kv_path(f"{path_screen_2_file}/{name_file}.kv") # Comentado pois estava duplicando os botões no widget logs_box

padding = 10


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


class RV(F.RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        # self.data = [{"text": str(x)} for x in range(100)]
        self.data = []


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
        Clock.schedule_once(self.animate_loading)
        Clock.schedule_interval(self.animate_loading, 1 / 2)
        Clock.schedule_interval(self.update_elapsed, 1 / 15)

    def animate_loading(self, *args):
        self.angle -= 360
        duration = 0.5
        animation = Animation(angle=self.angle, duration=duration)
        animation.start(self.ids.loading_icon)

    def update_elapsed(self, *args):
        elapsed = str(datetime.now() - self.begin)[2:11]
        self.ids.loading_label.text = f"Time elapsed: {elapsed}"


class LogsScreen(F.MDScreen):
    btns_widths = []
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

    async def get_all_logs(self):
        # session = asks.Session()
        session = create_session()
        response = await session.get(f"{self.BD_LINK}/Logs/.json")
        return response.json()

    async def async_open_calendar(self):
        results = await self.get_all_logs()
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

        date_dialog.bind(on_save=self.get_new_date)
        date_dialog.open()

    def go_to_top(self):
        recycleview = self.app.screen_manager.get_screen("Logs Screen").ids.recycleview
        recycleview.scroll_y = 1

    def go_to_bottom(self):
        recycleview = self.app.screen_manager.get_screen("Logs Screen").ids.recycleview
        recycleview.scroll_y = 0

    def get_new_date(self, instance, value, date_range):
        date = datetime.strftime(value, "%d-%m-%y")
        selected_date = datetime.strptime(date, "%d-%m-%y")
        if selected_date <= datetime.now():
            day = datetime.strftime(value, "%d")
            self.logscreen.ids.calendar_button_new.text_day = day

            month = datetime.strftime(value, "%m")
            self.logscreen.ids.calendar_button_new.text_month = month

            self.year = datetime.strftime(value, "%Y")
            self.date = date

            self.update_all_logs()
        else:
            self.app.nursery.start_soon(self.open_calendar)

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
            mainscreen = self.app.screen_manager.get_screen("Main Screen")
            btn = mainscreen.ids.accounts_btn
            text = btn.text
            return text
        except:
            return "GaloDoido"

    async def open_loading_popup(self, *args):
        self.angle = 0
        self.loading_popup = LoadingPopup()
        self.add_widget(self.loading_popup)

    def close_loading_popup(self, *args):
        if self.loading_popup != None:
            self.remove_widget(self.loading_popup)
            self.loading_popup = None

    def update_all_logs(self, dt=0):
        self.angle = 0
        self.app.nursery.start_soon(self.async_update_all_logs)

    async def async_update_all_logs(self):
        print(f"Updating logs to {self.account} on {self.date}")
        await self.open_loading_popup()

        new_logs = await self.async_get_new_logs()
        dict_all_logs = self.organize_logs(new_logs)

        self.clear_logs_box_widget()
        if dict_all_logs == None:
            self.logscreen.ids.no_logs_label.text = "No logs found"
            self.close_loading_popup()
            return None
        print(f"before add_logs: {datetime.now()}")

        # Adding logs to the RECYCLEVIEW
        for value in dict_all_logs[self.actual_filter]:
            self.ids.recycleview.data.append({"text": str(value)})
            self.current_logs.append(value)
        # await trio.sleep(5)

        self.logscreen.ids.no_logs_label.text = ""
        self.close_loading_popup()

    def update_current_logs(self, dt=0):
        self.app.nursery.start_soon(self.open_loading_popup)
        self.app.nursery.start_soon(self.async_update_current_logs)
        print("Updating current logs")

    async def async_update_current_logs(self, dt=0):
        # session = asks.Session()
        session = create_session()
        response = await session.get(f"{BDLINK}/Running_Info/.json")
        running_to_update = response.json()["running_to"]

        today = datetime.now().strftime("%d-%m-%y")
        if running_to_update != self.account or today != self.date:
            self.close_loading_popup()
            return
        print(f"Updating logs to {self.account} on {self.date}")
        new_logs = await self.async_get_new_logs()
        dict_all_logs = self.organize_logs(new_logs)
        if dict_all_logs == None:
            self.logscreen.ids.no_logs_label.text = "No logs found"
            self.close_loading_popup()
            return None
        fresh_current_logs = dict_all_logs[self.actual_filter]
        for fresh_log in fresh_current_logs:
            if fresh_log not in self.current_logs:
                self.ids.recycleview.data.append({"texto": str(fresh_log)})
                self.current_logs.append(fresh_log)

        self.logscreen.ids.no_logs_label.text = ""
        print("Updated!")
        self.close_loading_popup()

    def clear_logs_box_widget(self):
        self.ids.recycleview.data = []
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

    async def async_get_new_logs(self):
        # session = asks.Session()
        session = create_session()
        response = await session.get(
            f"{self.BD_LINK}/Logs/{self.date}/{self.account}/.json"
        )
        return response.json()

    def compare_logs(self, added_logs, actual_logs):
        new_logs = dict()

        # Comparing actual logs to old ones to identify new ones
        for log in actual_logs:
            if log not in added_logs:
                new_logs[log] = actual_logs[log]

        return new_logs

    def organize_logs(self, logs):
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
