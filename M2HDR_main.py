import os
import sys
import time
import shutil
import pyperclip
import serial.tools.list_ports
from pywinauto.keyboard import send_keys
from pywinauto.application import Application
from types import SimpleNamespace

import general_functions as fnc
import config_structure as config_structure
import DataSelectTesti as DataSelectTesti
import Sonuc as Sonuc

path_arview = r"C:\Program Files\ArView\ArView.exe"
base_path = os.path.dirname(os.path.abspath(__file__)) 

def launch_arview(path):
    app = Application(backend="uia").start(path)
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    return dlg

def device_sn(device_folder):
    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    devicesn_folder = os.path.join(base_path, device_folder)

    config_path = os.path.join(devicesn_folder, "config.txt")
    clipboard_content = pyperclip.paste()
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)


    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('DeviceSN'):
                return line.split('=', 1)[1].strip().strip('"')
    return None

def device_pn(device_folder):
    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)
    
    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    device_info_folder = os.path.join(base_path, device_folder)

    config_path = os.path.join(device_info_folder, "config.txt")
    clipboard_content = pyperclip.paste()
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)

    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('DevicePN'):
                return line.split('=', 1)[1].strip().strip('"')
    return None

def create_folder(base_path):

    relative_paths = [
        "Device",
        "Test Sonuclari",
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Acc Norm Testi", "Acilis Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Acc Norm Testi", "Dondurme Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Data Select"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Euler Kontrol Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Gyro Z Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Kalibrasyon Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Magn Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Reset Testi", "Hard Reset"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Reset Testi", "Soft Reset"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "GPS Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "Cift Anten Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "RTK Testi"),
        os.path.join("UretimSonrasiTesti", "M2HDR", "example_folder", "RS422 Testi"),
    ]

    for rel_path in relative_paths:
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(full_path, exist_ok=True)

def find_limit_file(pn_dvc, file_path):

    limit_file_path = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path = os.path.join(limit_file_path, f"{pn_dvc}_limitdegerleri_v00.txt")
    m2hdr_limitdegerleri_v00 = {}

    with open(limit_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, m2hdr_limitdegerleri_v00) 

    return m2hdr_limitdegerleri_v00


def M2HDR_main():
    #main

    pn_input = input("Sistemin etiketinde bulunan Part Number (PN) giriniz:")
    sn_input = input("Sistemin etiketinde bulunan Serial Number (SN) giriniz:")

    device_folder_name = "Device"

    create_folder(base_path)

    sn_dvc = device_sn(device_folder_name)
    pn_dvc = device_pn(device_folder_name)

    if pn_input == pn_dvc:
        if sn_input == sn_dvc:
            print("SN ve PN doğru")
        elif sn_input != sn_dvc:
            sys.exit("PN doğrudur. Sistemde yüklü olan ve etikette olan SN farklı")
    elif pn_input != pn_dvc:
        if sn_input == sn_dvc:
            sys.exit("SN doğrudur. Sistemde yüklü olan ve etikette olan PN farklı")
        elif sn_input != sn_dvc:
            sys.exit("Sistemde yüklü olan ve etikette olan PN ve SN farklı")

    limit_data = find_limit_file(pn_dvc, base_path)
    limits = SimpleNamespace(**limit_data)

    time.sleep(5)

    dlg = launch_arview(limits.arview_path) 
    
    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")

    #SN'ye uygun şekilde dosya aranır yoksa yeni dosya açılır
    uretim_folder_path = os.path.join(base_path, r"UretimSonrasiTesti")
    example_folder_path = os.path.join(uretim_folder_path, r"M2HDR")

    s3a_example_folder = os.path.join(example_folder_path, r"example_folder")
    s3a_sn_folder = os.path.join(example_folder_path, sn_dvc)

    try:
        shutil.copytree(s3a_example_folder, s3a_sn_folder)
    except FileExistsError:
        print(f"Dosya '{sn_dvc}' klasörde oluşturulmuştur")

    #Test - 1: Data Select Kontrol Testi
    print("***Test 1: Data Select Kontrol Testi")
    config_structure.config_structure_data_select_m2hdr(dlg, limits.checkbox_states_general)
    results_Data_Select = DataSelectTesti.DataSelectTest(dlg, sn_dvc, example_folder_path, limits.data_select_folder, limits.expected_columns_general, limits.sleep_time_data_select)
    #print("***Test 1: Data Select Kontrol Testi TAMAMLANDI")
    print(results_Data_Select["is_valid"])

    Sonuc.Sonuc(pn_dvc, sn_dvc, base_path, results_Data_Select)
    


if __name__ == "__main__":
    M2HDR_main()