from utils import load_kv_path
from kivy.factory import Factory as F
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import sp, dp
from kivymd.uix.behaviors import RectangularRippleBehavior
import os


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


class Filter(RectangularRippleBehavior, F.ButtonBehavior, F.BoxLayout):
    text = F.StringProperty("Botão")
    tamanho_da_fonte = F.NumericProperty(sp(18))
    icon = F.StringProperty("")
    cor_do_fundo = F.ColorProperty([1, 1, 1, 1])
    cor_da_fonte = F.ColorProperty([0, 0, 0, 1])
    cor_do_icone = F.ColorProperty([0, 0, 0, 1])
    raio_da_borda = F.ListProperty([dp(5)])


class LogsScreen(F.MDScreen):
    # Definindo lista com as larguras de todos os botões criados
    widths = []
    title = F.StringProperty()
    auto_scroll_on = True  # Ajustar para poder personalizar pelo app
    i = 0
    is_filters_screen_opened = False
    actual_filter = F.StringProperty()
    angle = F.NumericProperty(0)

    data = F.DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_enter(self):
        # logscreen = self.app.screen_manager.get_screen("Logs Screen")
        # mh = logscreen.ids.logs_box.minimum_height
        # print(mh)
        # print(f"Entrei na tela")
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
        # Clock.schedule_once(self.change_pause_color)  # ,5 para agendar para 5 segundos
        Clock.schedule_once(self.assign_function)

    def change_pause_color(self, dt):
        # self.data = {}
        logscreen = self.app.screen_manager.get_screen("Logs Screen")
        pause = logscreen.ids.topbar.right_action_items
        print("oi")
        print(type(pause))
        eval(f"({pause[0][1]})()")

    def get_account_name(self):
        try:
            self.app = App.get_running_app()
            mainscreen = self.app.screen_manager.get_screen("Main Screen")
            btn = mainscreen.ids.accounts_btn
            text = btn.text
            return text
        except:
            return "Account"

    def add_log(self):
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
            """# altura = log.height
            # dist_mantain_position = scrollview.convert_distance_to_scroll(0, altura)[1]
            # y_final = dist_mantain_position * altura
            # scrollview.scroll_y = y_final
            # print(f"altura {y_final}")"""
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
        scrollview.scroll_y = old_pos
        # scrollview.scroll_y *= 1 - dist_relativ_após_add"""

        # # Essa função printa a largura do log antes de renderizá-lo
        # print(f"log.width {log.width}")

        # print(f"log.get_button_width() {log.get_button_width()}")
        # print(logscreen.ids.log)

    def update_height(self, instance, *args):
        # Get the actual height of the widget (BoxLayout) after it is redrawn
        height = instance.minimum_height
        return height

    def clear_logs_box_widget(self):
        logscreen = self.app.screen_manager.get_screen("Logs Screen")
        logscreen.ids.logs_box.clear_widgets()

    def go_back_to_main_screen(self):
        # Change screen
        self.app = App.get_running_app()
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

    def open_filters_screen(self):
        if self.is_filters_screen_opened == False:
            self.filters_screen = FiltersSelection()

            for name in self.data:
                # Creating the custom button
                # btn = F.MDRectangleFlatIconButton(
                #     text=name,
                #     text_color=[0.3, 0.3, 0.3, 1],
                #     font_size=sp(12),
                #     icon=self.data[name][0],
                #     icon_color=[0, 0, 0, 1],
                #     icon_size=sp(30),
                #     line_width=1.05,
                #     line_color=[0, 0, 0, 1],
                #     md_bg_color=[1, 1, 1, 1],
                #     pos_hint={"center_x": 0.5},
                #     on_release=self.select_filter,
                # )
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
        self.actual_filter = button.text

        float_layout = self.ids.float_layout
        float_layout.remove_widget(self.filters_screen)
        self.is_filters_screen_opened = False

        animation = Animation(angle=0, duration=0.1)
        animation.start(self.ids.filter_button)
