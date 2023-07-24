import os
from kivy.lang import Builder
import requests
from sensitive_values import BDLINK, DDNS, SV_PORT


def load_kv_path(path):
    """
    Loads a kv file from a path
    """
    kv_path = os.path.join(os.getcwd(), path)
    if kv_path not in Builder.files:
        Builder.load_file(kv_path)


def contact_server(command, func_popup_server_off):
    # Send initiate command to server
    try:
        try:
            host = requests.get(f"{BDLINK}/Running_Info/.json").json()["Server_DNS"]
            req = requests.get(f"http://{host}:{SV_PORT}/{command}", timeout=5)
        except requests.exceptions.InvalidSchema:
            try:
                host = requests.get(f"{BDLINK}/Running_Info/.json").json()["Server_IP"]
                req = requests.get(f"http://{host}:{SV_PORT}/{command}", timeout=5)
            except requests.exceptions.InvalidSchema:
                return func_popup_server_off
        return req
    except:
        return "Comando enviado, mas sem resposta. Provavelmente funcionou (ou o servidor est'a ocupado rodando uma automaçao)!"
