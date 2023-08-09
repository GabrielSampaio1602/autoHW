import os
import ssl

import asks
import certifi
from kivy.app import App
from kivy.lang import Builder

from sensitive_values import BDLINK, DDNS, SV_PORT


def load_kv_path(path):
    """
    Loads a kv file from a path
    """
    kv_path = os.path.join(os.getcwd(), path)
    if kv_path not in Builder.files:
        Builder.load_file(kv_path)


def create_session():
    """
    Creates a session
    """
    return asks.Session(
        connections=1,
        ssl_context=ssl.create_default_context(cafile=certifi.where()),
    )


def contact_server(app, command, func_popup_server_off):
    res = app.nursery.start_soon(async_contact_server, command, func_popup_server_off)
    print(res)
    return res


# async def async_contact_server(command, func_popup_server_off):
async def async_contact_server(command: str):
    # Send initiate command to server
    # session = asks.Session()
    session = create_session()
    try:
        try:
            # host = requests.get(f"{BDLINK}/Running_Info/.json").json()["Server_DNS"]
            # req = requests.get(f"http://{host}:{SV_PORT}/{command}", timeout=5)
            requisicao_host = await session.get(f"{BDLINK}/Running_Info/.json")
            host = requisicao_host.json()["Server_DNS"]
            # req = await session.get(f"http://{host}:{SV_PORT}/{command}", timeout=5)
            req = await session.get(f"http://{host}:{SV_PORT}/{command}", timeout=1)
            print("Command sent to server's DNS!")
        # except requests.exceptions.InvalidSchema:
        except Exception as e:
            print(e)
            try:
                # host = requests.get(f"{BDLINK}/Running_Info/.json").json()["Server_IP"]
                # req = requests.get(f"http://{host}:{SV_PORT}/{command}", timeout=5)
                requisicao_host = await session.get(f"{BDLINK}/Running_Info/.json")
                host = requisicao_host.json()["Server_IP"]
                # req = await session.get(f"http://{host}:{SV_PORT}/{command}", timeout=5)
                req = await session.get(f"http://{host}:{SV_PORT}/{command}", timeout=1)
                print("Couldn't send to DNS. Command sent to server's IP!")
            # except requests.exceptions.InvalidSchema:
            except Exception as e:
                print(e)
                print("Server offline!")
                # return func_popup_server_off
                return None
        return req
    except:
        print(
            "Comando enviado, mas sem resposta. Provavelmente funcionou (ou o servidor está ocupado rodando uma automaçao)!"
        )
        return "Comando enviado, mas sem resposta. Provavelmente funcionou (ou o servidor está ocupado rodando uma automaçao)!"
