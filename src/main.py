import sys
import traceback
import time
import usb.core

# 設定ファイル関連
import tomllib
from pathlib import Path
import importlib


# 以下の USB デバイスは無視する
EXCLUDE_VID = [
    # LINUX_VID (root hub が該当する場合)
    0x1D6B,
    # GOOGLE_VID (すでにAOAになっている場合)
    0x18D1,
]

PID_AOA = 0x2D00
PID_AOA_ADB = 0x2D01


# aoa 確立後の通信を行うモジュール
protocol_module = None


# 設定の読み込み
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.toml"

while True:
    try:
        with open(CONFIG_FILE, "rb") as f:
            config = tomllib.load(f)
            protocol_module = importlib.import_module(config["protocol"]["module"])
            break
    except Exception as e:
        print(f"{CONFIG_FILE} load error:", e)
        time.sleep(30)
    




# 接続されているUSBデバイスを出力
def output_all_devices():
    devices = usb.core.find(find_all=True)
    for n in devices:
        print("---")
        print("VID: " + format(n.idVendor, '#010x'))
        print("PID: " + format(n.idProduct, '#010x'))
        print("DeviceClass: " + format(n.bDeviceClass, '#010x'))


# 接続しているUSBデバイスを取得
def get_connected_device():
    for n in usb.core.find(find_all=True):
        # hub の検出 (ハブは除外)
        if n.bDeviceClass == 0x09:
            continue

        # print("VID: " + format(n.idVendor, '#010x'))
        # print("PID: " + format(n.idProduct, '#010x'))
        if n.idVendor in EXCLUDE_VID:
            continue
        else:
            return n
    return None


# AOA接続しているデバイスを取得
def get_connected_aoa_device():
    for n in usb.core.find(find_all=True):
        if n.idProduct == PID_AOA or n.idProduct == PID_AOA_ADB:
            return n
    return None


# AndroidへAOAの情報を送信する
def set_aoa_info(device):
    # aoa version の取得
    response = device.ctrl_transfer(
        0xC0, # bmRequestType
        51, # bRequest
        0, # wValue
        0, # wIndex
        2, #data_or_wLength
        timeout=None)
    print("received data: ", response)

    aoa_version = (response[1] << 8) + response[0]
    print("aoa_version: ", aoa_version)

    if aoa_version < 0:
        print("aoa not supported")
        return False

    # AOAデバイスの情報
    accessory = config.get("accessory", {})
    manufacturer = accessory.get("manufacturer", "")
    model_name = accessory.get("model_name", "")
    description = accessory.get("description", "")
    version = accessory.get("version", "")
    uri = accessory.get("url", "")
    serial_number = accessory.get("serial_number", "")

    print(f"""
send accessory info:
* manufactorer: {manufacturer}
* model_name: {model_name}
* description: {description}
* version: {version}
* uri: {uri}
* serial_number: {serial_number}
    """)

    # send
    response = device.ctrl_transfer(0x40, 52, 0, 0, manufacturer, timeout=None)
    print("manu response:", response)
    response = device.ctrl_transfer(0x40, 52, 0, 1, model_name, timeout=None)
    print("model response:", response)
    response = device.ctrl_transfer(0x40, 52, 0, 2, description, timeout=None)
    print("desc response:", response)
    response = device.ctrl_transfer(0x40, 52, 0, 3, version, timeout=None)
    print("ver response:", response)
    response = device.ctrl_transfer(0x40, 52, 0, 4, uri, timeout=None)
    print("uri response:", response)
    response = device.ctrl_transfer(0x40, 52, 0, 5, serial_number, timeout=None)
    print("sn response:", response)

    return True


# AOAモードへ切り替え指示を送信
def set_change_aoa_mode(device):
    # DeviceをAccessory modeにする
    response = device.ctrl_transfer(0x40, 53, 0, 0, 0, timeout=None)
    print("response:", response)
    #   if(response < 0){error(response);return -1;}


# 入出力のエンドポイントを取得
def get_endpoints(device):
    # Find the first interface and its endpoints
    cfg = device.get_active_configuration()
    intf = cfg[(0,0)]

    ep_in = None
    ep_out = None

    for e in usb.util.find_descriptor(intf, find_all=True):
        dir = usb.util.endpoint_direction(e.bEndpointAddress)
        if ep_in is None and dir == usb.util.ENDPOINT_IN:
            ep_in = e

        if ep_out is None and dir == usb.util.ENDPOINT_OUT:
            ep_out = e

        if ep_in is not None and ep_out is not None:
            break

    return ep_in, ep_out



while True:
    device_aoa = None
    endpoint_in = None
    endpoint_out = None

    # アクセサリモードのデバイスを探して使用する
    # 見つからない場合は、接続中のデバイスを探して、アクセサリモードに変更する
    while device_aoa is None:
        device_aoa = get_connected_aoa_device()
        if isinstance(device_aoa, usb.core.Device):
            break

        device = get_connected_device()
        if isinstance(device, usb.core.Device):
            print("# found connected usb device. change to aoa_mode.")
            print("* VID: " + format(device.idVendor, '#010x'))
            print("* PID: " + format(device.idProduct, '#010x'))
 
            try: 
                set_aoa_info(device)
                set_change_aoa_mode(device)

                time.sleep(1)
                # PID が変わるので現在のデバイスは不要
                usb.util.dispose_resources(device)
            except usb.core.USBError as e:
                print(" error:", e)

    print("# found aoa device")
    print("* VID: " + format(device_aoa.idVendor, '#010x'))
    print("* PID: " + format(device_aoa.idProduct, '#010x'))


    # 入出力用のエンドポイントを取得
    # - device_aoa.ctrl_transfer(address,..) でも通信できるようだが、どうもアドレスが変わる場合があるようなので取得する
    print("# get endpoints")
    try:
        endpoint_in, endpoint_out = get_endpoints(device_aoa)
        if endpoint_in is None or endpoint_out is None:
            print("endpoint not found")
            continue
    except Exception as e:
        print("get_endpoints error: ", e)
        # error == 19 is "no such device" (切断直後に見られる) (android が aoa のまま再接続することもある.)
        if isinstance(e, usb.core.USBError) and e.errno == 19: time.sleep(1)

    print("* endpoint in:", endpoint_in)
    print("* endpoint out:", endpoint_out)


    # 通信
    print("# communicate")
    try:
        protocol_module.communicate(device_aoa, endpoint_in, endpoint_out, config["protocol"])
    except Exception as e:
        print("communicate error: ", e)
        traceback.print_exc()
        # error == 19 is "no such device" (切断直後に見られる) (android が aoa のまま再接続することもある.)
        if isinstance(e, usb.core.USBError) and e.errno == 19: time.sleep(1)
    finally:
        usb.util.dispose_resources(device_aoa)

