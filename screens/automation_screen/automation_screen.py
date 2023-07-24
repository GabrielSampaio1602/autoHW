from utils import load_kv_path, contact_server
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
from sensitive_values import MAC, IP, PORT, SV_PORT, EXE_PATH, BDLINK, DDNS
from wakeonlan import send_magic_packet
import json
from HWAppTrigger import send_command

# icons link: https://pictogrammers.com/library/mdi/

paths_folder = os.path.dirname(__file__)
inicio_screens = paths_folder.find("screens")
path_screen_2_file = paths_folder[inicio_screens:]

name_file = os.path.basename(__file__)[:-3]
# load_kv_path(f"{path_screen_2_file}/{name_file}.kv") # Comentado pois estava duplicando os botões no widget logs_box

padding = 10


class SectionButton(RectangularRippleBehavior, F.ButtonBehavior, F.FloatLayout):
    text = F.StringProperty("Botão")
    tamanho_da_fonte = F.NumericProperty(sp(18))
    icon = F.StringProperty("")
    cor_do_fundo = F.ColorProperty([1, 1, 1, 1])
    cor_da_fonte = F.ColorProperty([0, 0, 0, 1])
    cor_do_icone = F.ColorProperty([0, 0, 0, 1])
    raio_da_borda = F.ListProperty([dp(5)])


class HostConfiguration(F.BoxLayout):
    ip_text = F.StringProperty()
    mac_text = F.StringProperty()
    port_text = F.StringProperty()
    sv_port_text = F.StringProperty()
    exe_path_text = F.StringProperty()
    bd_link_text = F.StringProperty()

    def __init__(
        self,
        ip_text=IP,
        mac_text=MAC,
        port_text=PORT,
        sv_port_text=SV_PORT,
        exe_path_text=EXE_PATH,
        bd_link_text=BDLINK,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ip_text = ip_text
        self.mac_text = mac_text
        self.port_text = port_text
        self.sv_port_text = sv_port_text
        self.exe_path_text = exe_path_text
        self.bd_link_text = bd_link_text


class SectionList(F.GridLayout):
    pass


class SectionItem(RectangularRippleBehavior, F.ButtonBehavior, F.FloatLayout):
    pass


class AutomationScreen(F.MDScreen):
    data = F.DictProperty()

    accounts = F.ListProperty()
    functions = F.ListProperty()
    wait_before = F.NumericProperty(0)
    wait_after = F.NumericProperty(0)
    times_to_run = F.NumericProperty(1)
    hibernate = F.BooleanProperty(True)

    acc1 = F.BooleanProperty(True)
    acc2 = F.BooleanProperty(True)
    acc3 = F.BooleanProperty(True)
    accs_var_list = F.ListProperty([acc1, acc2, acc3])

    func1 = F.BooleanProperty(True)
    func2 = F.BooleanProperty(True)
    func3 = F.BooleanProperty(True)
    func4 = F.BooleanProperty(True)
    func5 = F.BooleanProperty(True)
    func6 = F.BooleanProperty(True)
    func7 = F.BooleanProperty(True)
    func8 = F.BooleanProperty(True)
    func9 = F.BooleanProperty(True)
    func10 = F.BooleanProperty(True)
    func11 = F.BooleanProperty(True)
    func12 = F.BooleanProperty(True)
    funcs_var_list = F.ListProperty(
        [
            func1,
            func2,
            func3,
            func4,
            func5,
            func6,
            func7,
            func8,
            func9,
            func10,
            func11,
            func12,
        ]
    )

    ip = IP
    mac = MAC
    port = PORT
    sv_port = SV_PORT
    exe_path = EXE_PATH
    bd_link = BDLINK

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_enter(self):
        self.automationscreen = self.app.screen_manager.get_screen("Automation Screen")
        # Clock.schedule_once(self.assign_function)

        # Clock.schedule_once(self.change_pause_color)  # ,5 para agendar para 5 segundos
        # Clock.schedule_once(self.assign_function)
        # Clock.schedule_once(self.update_all_logs, 5)

        # call update_current_logs every 60 seconds
        # Clock.schedule_interval(self.update_current_logs, 60)
        # Clock.schedule_once(self.assign_day_month)

        from kivy.base import EventLoop

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *args):
        # print(key)
        # print(window)
        if (
            key in [27, 1001] and self.app.screen_manager.current == "Automation Screen"
        ):  # 27 = ESC # 1001 = BACK_ANDROID
            self.app = App.get_running_app()
            previous_screen = self.app.screen_manager.previous()
            print(previous_screen)  # >> Main Screen
            self.app.change_screen(previous_screen, "right")
            return True  # Overwrite the default behavior (default: close window)

    def go_back_to_main_screen(self):
        # Change screen
        self.app = App.get_running_app()
        self.app.change_screen("Main Screen", "right")

    # def assign_function(self, dt):
    # self.automationscreen.ids.acc_section_btn.on_release = self.open_section
    # print(self.automationscreen.ids.acc_section_btn.on_release)
    # self.automationscreen.ids.topbar.right_action_items

    def dis_enable_items(self, widget, container_id, action=""):
        for id in self.automationscreen.ids:
            if id == container_id:
                container = self.automationscreen.ids[id]

        for item in list(container.walk()):
            try:
                if item.section == widget.text and action == "open":
                    item.disabled = False
                elif item.section == widget.text and action == "close":
                    item.disabled = True
            except:
                pass

        if action == "open":
            container.height = container.minimum_height
            container.opacity = 1
        if action == "close":
            container.height = 0
            container.opacity = 0

    def rotate_icon(self, widget):
        # print(widget.children)
        if int(widget.angle) in [0, 360]:
            widget.angle = 0 if widget.angle == 360 else 0
            animation = Animation(angle=180, duration=0.1)
            animation.start(widget)
            widget.angle = 180
            action = "open"
        else:
            animation = Animation(angle=360, duration=0.1)
            animation.start(widget)
            widget.angle = 0
            action = "close"

        if widget.text == "Accounts":
            box_id = "box_accs"
        elif widget.text == "Functions":
            box_id = "box_funcs"
        elif widget.text == "Wait Before":
            box_id = "wait_bef_accs"
        elif widget.text == "Wait After":
            box_id = "wait_aft_accs"
        elif widget.text == "Times to Run":
            box_id = "times_run_accs"
        self.dis_enable_items(widget, box_id, action)

    def change_hibernate(self):
        self.hibernate = not self.hibernate  # Invert boolean value

        self.automationscreen = self.app.screen_manager.get_screen("Automation Screen")
        hibernate_switch = self.automationscreen.ids.hibernate_btn
        if not self.hibernate:
            hibernate_switch.icon = "toggle-switch-off"
            hibernate_switch.cor_do_icone = [0, 0, 0, 0.3]
        else:
            hibernate_switch.icon = "toggle-switch"
            hibernate_switch.cor_do_icone = [0, 0.5, 0, 1]

    def change_status(self, widget):
        # Alterar ícone para a esquerda (animação) e trocar a cor para cinza // Can't animate strings objects
        # animation = Animation(switch_icon="toggle-switch-off")
        # animation &= Animation(
        #     switch_color=list([0.4, 0.4, 0.4, 1]),
        #     duration=0.1,
        # )
        # animation.start(widget)

        # Alterar o valor associado àquele widget
        # for var in self.accs_var_list + self.funcs_var_list:
        #     if widget.var_name == var.name:
        #         # var = not var
        #         # var = False if var == False else True
        #         if var == False:
        #             var = True
        #         else:
        #             var = False
        #         print(var)
        # print(self.accs_var_list)
        # print([var.name for var in self.accs_var_list])

        # print(getattr(self, widget.var_name))
        # setattr(self, widget.var_name, False) if getattr(
        #     self, widget.var_name
        # ) == True else setattr(self, widget.var_name, True)
        # print(getattr(self, widget.var_name))

        if getattr(self, widget.var_name) == True:
            # Changing value to False (the other ways didn't work)
            setattr(self, widget.var_name, False)
            widget.switch_icon = "toggle-switch-off"
            widget.switch_color = [0.4, 0.4, 0.4, 1]
        else:
            setattr(self, widget.var_name, True)
            widget.switch_icon = "toggle-switch"
            widget.switch_color = [0, 0.5, 0, 0.9]

    def change_all_status(self, btn):
        check_all = True if btn.text == "Check All" else False
        all_widgets = list(self.automationscreen.walk())
        for item in all_widgets:
            has_var_name = "var_name" in item.__dir__()  # get object attributes
            if has_var_name:
                if "func" in item.var_name:
                    if check_all:
                        setattr(self, item.var_name, True)
                        item.switch_icon = "toggle-switch"
                        item.switch_color = [0, 0.5, 0, 0.9]
                        btn.md_bg_color = [0.6, 0.6, 0.6, 1]
                        btn.text_color = [0, 0, 0, 0.8]
                    else:
                        setattr(self, item.var_name, False)
                        item.switch_icon = "toggle-switch-off"
                        item.switch_color = [0.4, 0.4, 0.4, 1]
                        btn.md_bg_color = [0, 0.6, 0, 1]
                        btn.text_color = [1, 1, 1, 0.8]
        if check_all:
            btn.text = "Uncheck All"
        else:
            btn.text = "Check All"

        # if getattr(self, widget.var_name) == True:
        #     # Changing value to False (the other ways didn't work)
        #     setattr(self, widget.var_name, False)
        #     widget.switch_icon = "toggle-switch-off"
        #     widget.switch_color = [0.4, 0.4, 0.4, 1]
        # else:
        #     setattr(self, widget.var_name, True)
        #     widget.switch_icon = "toggle-switch"
        #     widget.switch_color = [0, 0.5, 0, 0.9]

    def get_selected_parameters(self):
        # for var in self.accs_var_list + self.funcs_var_list:
        #     if "acc" in var.name and var == True:
        #         name = ""
        #         self.accounts.append()
        #     elif "func" in var.name and var == True:
        #         func = ""
        #         self.functions.append()
        self.accounts = []
        self.functions = []

        for item in list(self.automationscreen.walk()):
            has_var_name = "var_name" in item.__dir__()
            if has_var_name:  # get object attributes
                is_true = getattr(self, item.var_name) == True
                if "acc" in item.var_name and is_true:
                    self.accounts.append(item.parameter_name)
                elif "func" in item.var_name and is_true:
                    self.functions.append(item.parameter_name)

        if len(self.accounts) == 0:
            # print("Select at least one account")
            self.dialog = F.MDDialog(
                text="Select at least one account!",
                buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
            )
            # dialog_btn.bind(on_release=dialog.dismiss())
            self.dialog.open()
            return "error"
        elif len(self.functions) == 0:
            # print("Select at least one function")
            self.dialog = F.MDDialog(
                text="Select at least one function!",
                buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
            )
            # dialog_btn.bind(on_release=dialog.dismiss())
            self.dialog.open()
        else:
            return (
                self.accounts,
                self.functions,
                self.hibernate,
                self.wait_before,
                self.wait_after,
                self.times_to_run,
            )

    def dismiss_popup(self, popup):
        self.dialog.dismiss()

    def popup_server_off(self):
        self.dialog = F.MDDialog(
            text=f"The server is offline or isn't ready yet. Please try again in a few minutes or check if it's really on",
            buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
            anchor_x="center",
        )
        self.dialog.open()

    def start_automation(self):
        running_to_update = requests.get(f"{BDLINK}/Running_Info/.json").json()[
            "running_to"
        ]
        if running_to_update == "None":
            # Wake PC on LAN - Mesma rede
            send_magic_packet(self.mac, ip_address=self.ip, port=int(self.port))
            # Wake PC on WAN - Rede externa
            send_magic_packet(self.mac, ip_address=DDNS, port=int(self.port))
            # send_magic_packet(mac,interface=ip)

            # Send info to BD
            parameters = self.get_selected_parameters()
            if parameters != "error":
                (
                    accs_selected,
                    functions_selected,
                    hibernate,
                    wait_before,
                    wait_after,
                    times_to_run,
                ) = parameters

                requests.patch(
                    f"{BDLINK}/Running_Info/.json",
                    data=json.dumps(
                        {
                            "accs_selected": accs_selected,
                            "functions_selected": functions_selected,
                            "hibernate": hibernate,
                            "wait_before": wait_before,
                            "wait_after": wait_after,
                            "times_to_run": times_to_run,
                            "running_trigger": "App",
                        }
                    ),
                )

                req = contact_server("rodar", self.popup_server_off)

                # result = req
                # message = req.text
                # print(result, message)
                # self.dialog = F.MDDialog(
                #     text=message,
                #     buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
                # )
                # self.dialog.open()

                # if result == True:
                #     self.app.change_screen("Main Screen", "right")

                # print(self.get_selected_parameters())
        else:
            self.dialog = F.MDDialog(
                text=f"The automation is currently running to {running_to_update}.\n\nPlease wait until it's finished!",
                buttons=[F.MDFlatButton(text="OK", on_release=self.dismiss_popup)],
                anchor_x="center",
            )
            self.dialog.open()

    def configure_host(self):
        self.dialog = F.MDDialog(
            title="Configure HOST:",
            # text=message,
            type="custom",
            content_cls=HostConfiguration(
                self.ip, self.mac, self.port, self.sv_port, self.exe_path, self.bd_link
            ),
            buttons=[
                F.MDFlatButton(text="Cancel", on_release=self.dismiss_popup),
                F.MDFlatButton(
                    text="Save", text_color=[0, 0.6, 0, 1], on_release=self.save
                ),
            ],
        )
        self.dialog.open()

    def save(self, *args):
        # print(self.dialog.content_cls.__dir__())
        # print(self.dialog.title)

        self.ip = self.dialog.content_cls.ids.ip.text
        self.mac = self.dialog.content_cls.ids.mac.text
        self.port = self.dialog.content_cls.ids.port.text
        self.sv_port = self.dialog.content_cls.ids.sv_port.text
        self.exe_path = self.dialog.content_cls.ids.exe_path.text
        self.bd_link = self.dialog.content_cls.ids.bd_link.text

        # PATCH INFO ON BD

        self.dismiss_popup(self.dialog)
