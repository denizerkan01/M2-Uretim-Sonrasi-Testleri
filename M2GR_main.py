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
import KalibrasyonKontrolTesti as KalibrasyonKontrolTesti
import M2GR_ResetTesti as M2GR_ResetTesti
import M2GR_AccNormGyroAcilisTesti as M2GR_AccNormGyroAcilisTesti
import M2GR_AccDondurme as M2GR_AccDondurmeTesti
import M2GR_EulerKontrolTesti as M2GR_EulerKontrolTesti
import M2GR_GyroZTesti as M2GR_GyroZTesti
import RS422_232Testi as RS422_232Testi
import Anten_Testi as Anten_Testi
import M2GR_RTK_Testi as M2GR_RTK_Testi
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
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")
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
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")
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
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Acc Norm Testi", "Acilis Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Acc Norm Testi", "Dondurme Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Data Select"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Euler Kontrol Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Gyro Z Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Kalibrasyon Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Magn Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Reset Testi", "Hard Reset"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "Reset Testi", "Soft Reset"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "GPS Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "RTK Testi"),
        os.path.join("UretimSonrasiTesti", "M2GR", "example_folder", "RS422 Testi"),
    ]

    for rel_path in relative_paths:
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(full_path, exist_ok=True)

def find_limit_file(pn_dvc, file_path):

    limit_file_path = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path = os.path.join(limit_file_path, f"{pn_dvc}_limitdegerleri_v00.txt")
    m2gr_limitdegerleri_v00 = {}

    with open(limit_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, m2gr_limitdegerleri_v00) 

    return m2gr_limitdegerleri_v00


def M2GR_main():
    #main

    pn_input = os.environ.get("M2GR_LABEL_PN") or input("Sistemin etiketinde bulunan Part Number (PN) giriniz:")
    sn_input = os.environ.get("M2GR_LABEL_SN") or input("Sistemin etiketinde bulunan Serial Number (SN) giriniz:")

    device_folder_name = "Device"

    create_folder(base_path)

    sn_dvc = device_sn(device_folder_name)
    pn_dvc = device_pn(device_folder_name)

    print(f"GUI_DEVICE|pn_dvc|{pn_dvc or ''}")
    print(f"GUI_DEVICE|sn_dvc|{sn_dvc or ''}")
    print(f"GUI_DEVICE|pn_match|{str(pn_input == pn_dvc).lower()}")
    print(f"GUI_DEVICE|sn_match|{str(sn_input == sn_dvc).lower()}")

    if pn_input == pn_dvc:
        if sn_input == sn_dvc:
            print("SN ve PN doğru")
            print("GUI_INFO|custom|Sisteme ait SN ve PN ile girilen SN ve PN eşleşmektedir.")
        elif sn_input != sn_dvc:
            print("GUI_INFO|custom|Sisteme ait SN ile girilen SN eşleşmemektedir.")
            sys.exit("PN doğrudur. Sistemde yüklü olan ve etikette olan SN farklı")
    elif pn_input != pn_dvc:
        if sn_input == sn_dvc:
            print("GUI_INFO|custom|Sisteme ait PN ile girilen PN eşleşmemektedir.")
            sys.exit("SN doğrudur. Sistemde yüklü olan ve etikette olan PN farklı")
        elif sn_input != sn_dvc:
            print("GUI_INFO|custom|Sisteme ait SN ve PN ile girilen SN ve PN eşleşmemektedir.")
            sys.exit("Sistemde yüklü olan ve etikette olan PN ve SN farklı")

    limit_data = find_limit_file(pn_dvc, base_path)
    limits = SimpleNamespace(**limit_data)

    time.sleep(5)

    dlg = launch_arview(limits.arview_path) 
    
    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)
    print(f"GUI_PORT|standard|{target_standard or ''}")

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        print("GUI_CONNECTION|false")
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")
        sys.exit("!!! Can't Connect to the Device !!!")
    print("GUI_CONNECTION|true")

    #SN'ye uygun şekilde dosya aranır yoksa yeni dosya açılır
    uretim_folder_path = os.path.join(base_path, r"UretimSonrasiTesti")
    example_folder_path = os.path.join(uretim_folder_path, r"M2GR")

    s3a_example_folder = os.path.join(example_folder_path, r"example_folder")
    s3a_sn_folder = os.path.join(example_folder_path, sn_dvc)

    try:
        shutil.copytree(s3a_example_folder, s3a_sn_folder)
    except FileExistsError:
        print(f"Dosya '{sn_dvc}' klasörde oluşturulmuştur")

    #Test - 1: Data Select Kontrol Testi
    print("***Test 1: Data Select Kontrol Testi")
    config_structure.config_structure_data_select_m2gr(dlg, limits.checkbox_states_general)
    results_Data_Select = DataSelectTesti.DataSelectTest(dlg, sn_dvc, example_folder_path, limits.data_select_folder, limits.expected_columns_general, limits.sleep_time_data_select)
    print(f"GUI_RESULT|01|{str(bool(results_Data_Select.get('is_valid'))).lower()}")
    print("***Test 1: Data Select Kontrol Testi TAMAMLANDI")
    
    print("***Test 2: Kalibrasyon Kontrol Testi")
    config_structure.config_structure_kalibrasyon_kontrol_s3a(dlg, limits.checkbox_states_general)
    #results_Kalibrasyon_Kontrol = KalibrasyonKontrolTesti.KalibrasyonKontrolTesti(dlg, example_folder_path, sn_dvc, limits.hw_num, limits.firmware_version, limits.device_name, limits.ref_matrix_acc, limits.ref_matrix_gyro, limits.ref_matrix_magn, limits.kalibrasyon_kontrol_folder)    
    results_Kalibrasyon_Kontrol = KalibrasyonKontrolTesti.KalibrasyonKontrolTesti(dlg, example_folder_path, sn_dvc, limits.hw_num, limits.firmware_version, limits.device_name, limits.ref_matrix_acc, limits.ref_matrix_gyro,  limits.kalibrasyon_kontrol_folder)
    print(f"GUI_RESULT|02|{str(bool(results_Kalibrasyon_Kontrol.get('calib_ctrl_success'))).lower()}")
    print(f"GUI_INFO|firmware_version_match|{str(bool(results_Kalibrasyon_Kontrol.get('firmware_version_match'))).lower()}")
    print(f"GUI_INFO|acc_is_calibrated|{str(bool(results_Kalibrasyon_Kontrol.get('acc_is_calibrated'))).lower()}")
    print(f"GUI_INFO|gyro_is_calibrated|{str(bool(results_Kalibrasyon_Kontrol.get('gyro_is_calibrated'))).lower()}")

    if results_Kalibrasyon_Kontrol["acc_is_calibrated"] == False:
        sys.exit("Sistemde Acc kalibrasyonu bulunmamaktadır. Test yapılamaz")

    if results_Kalibrasyon_Kontrol["gyro_is_calibrated"] == False:
        sys.exit("Sistemde Gyro kalibrasyonu bulunmamaktadır. Test yapılamaz")
        
    print("***Test 2: Kalibrasyon Kontrol Testi TAMAMLANDI")

    # Test 3: Reset Testi
    print("***Test 3: Reset Testi")
    config_structure.config_structure_acc_norm_gyro_acilis(dlg, limits.checkbox_states_general)
    results_Reset = M2GR_ResetTesti.M2GR_ResetTesti(dlg, sn_dvc, example_folder_path, limits.hard_reset_folder, limits.soft_reset_folder, limits.sleep_time_reset_testi)
    print(f"GUI_RESULT|03|{str(bool(results_Reset.get('reset_result'))).lower()}")
    print("***Test 3: Reset Testi TAMAMLANDI")

    # Test 4: ACC Norm ve Gyro Açılış Testi
    print("***Test 4: Acc Norm ve Gyro Açılış Testi")
    config_structure.config_structure_acc_norm_gyro_acilis(dlg, limits.checkbox_states_general)
    results_Acc_Acilis = M2GR_AccNormGyroAcilisTesti.M2GR_AccNormGyroAcilisTesti(dlg, sn_dvc, example_folder_path, limits.acc_acilis_folder, limits.acc_acilis_successfull_needed, limits.max_ok_acc_norm_value, limits.min_ok_acc_norm_value, limits.max_best_acc_norm_value, limits.min_best_acc_norm_value, limits.sleep_time_acc_norm_gyro_acilis)
    print(f"GUI_RESULT|04|{str(bool(results_Acc_Acilis.get('CalibrationSuccess') and results_Acc_Acilis.get('gyro_acilis_success'))).lower()}")
    print("***Test 4: Acc Norm ve Gyro Açılış Testi TAMAMLANDI")

    #Test 5: Acc Döndürme Testi
    print("***Test 5: Acc Döndürme Testi")
    config_structure.config_structure_acc_norm_gyro_acilis(dlg, limits.checkbox_states_general)
    results_Acc_Dondurme = M2GR_AccDondurmeTesti.M2GR_AccDondurmeTesti(dlg, sn_dvc, example_folder_path, limits.acc_dondurme_folder, 0.5, 0.5, limits.sleep_time_acc_dondurme)
    print(f"GUI_RESULT|05|{str(bool(results_Acc_Dondurme.get('AccDondurmeSuccess'))).lower()}")
    print("***Test 5: Acc Döndürme Testi TAMAMLANDI")
    print(results_Acc_Dondurme)

    #Test 6: Euler Kontrol Testi
    print("***Test 6: Euler Kontrol Testi")
    config_structure.config_structure_acc_norm_gyro_acilis(dlg, limits.checkbox_states_general)
    results_Euler_Kontrol = M2GR_EulerKontrolTesti.M2GR_EulerKontrolTesti(dlg, sn_dvc, example_folder_path, limits.euler_kontrol_folder, limits.euler_kontrol_folder, limits.max_roll_value, limits.min_roll_value, limits.max_pitch_value, limits.min_pitch_value, limits.sleep_time_euler_kontrol)
    print(f"GUI_RESULT|06|{str(bool(results_Euler_Kontrol.get('EulerSuccess'))).lower()}")
    print("***Test 6: Euler Kontrol Testi TAMAMLANDI")

    #Test 7: Gyro Z Testi
    print("***Test 7: Gyro Z Testi")
    config_structure.config_structure_gyroz(dlg, limits.checkbox_states_general, limits.checkbox_states_target_meas_gyroz_testi)
    results_Gyro_Z = M2GR_GyroZTesti.M2GR_GyroZTesti(dlg, sn_dvc, example_folder_path, limits.gyro_z_folder, limits.sleep_time_gyroz)
    print(f"GUI_RESULT|07|{str(bool(results_Gyro_Z and results_Gyro_Z.get('GyroZSucess'))).lower()}")
    print("***Test 7: Gyro Z Testi TAMAMLANDI")

    #Test 8: Bağlantı Testi
    print("***Test 8: Bağlantı Testi")
    ports = list(serial.tools.list_ports.comports())
    target_enhanced = fnc.find_port("Enhanced", ports)
    print(f"GUI_PORT|enhanced|{target_enhanced or ''}")
    results_conn = RS422_232Testi.RS422_232Testi(dlg, example_folder_path, sn_dvc, limits.hw_num, limits.firmware_version, limits.device_name, limits.ref_matrix_acc, limits.ref_matrix_gyro, limits.ref_matrix_magn, limits.kalibrasyon_kontrol_folder)
    print(f"GUI_RESULT|08|{str(bool(results_conn.get('result_conn'))).lower()}")
    print("***Test 8: Bağlantı Testi TAMAMLANDI")
    """
    #Test 9: Anten Testi

    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    print("Anten takınız")

    anten_input = input("Sisteme anten takıldı mı?(y/n)")

    if anten_input == 'y':
        print("yes")
    elif anten_input == 'n':
        print("no")
        print("Anten takın")
        anten_input2 = input("Sisteme anten takıldı mı?(y/n)")
        if anten_input2 == 'y':
            print("yes2")
        else:
            print(":()")
    

    dlg = launch_arview(limits.arview_path) 
        
    ports = list(serial.tools.list_ports.comports())
        
    target_standard = fnc.find_port("Standard", ports)
    
    if not fnc.try_connect(dlg, target_standard, "Standard"):
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")
        sys.exit("!!! Can't Connect to the Device !!!")

    print("***Test 9: GPS Testi")
    results_GPS = Anten_Testi.Anten_Testi(dlg, sn_dvc, example_folder_path,  limits.sleep_time_gps, limits.gps_testi_id, limits.gps_folder)
    print("***Test 9: GPS Testi TAMAMLANDI")

    print("***Test 10: RTK Testi")
    config_structure.config_structure_acc_norm_gyro_acilis(dlg, limits.checkbox_states_general)
    results_RTK = M2GR_RTK_Testi.M2GR_RTK_Testi(dlg, sn_dvc, example_folder_path, limits.rtk_folder, limits.sleep_time_rtk, limits.low_rate_rtk_id)
    print("***Test 10: RTK Testi TAMAMLANDI")"""

    #Sonuc.Sonuc(pn_dvc, sn_dvc, base_path, results_Data_Select, results_Kalibrasyon_Kontrol, results_Reset, results_Acc_Acilis, results_Acc_Dondurme, results_Euler_Kontrol, results_Gyro_Z, results_conn, results_GPS, results_RTK)
    Sonuc.Sonuc(pn_dvc, sn_dvc, base_path, results_Data_Select, results_Kalibrasyon_Kontrol, results_Reset, results_Acc_Acilis, results_Acc_Dondurme, results_Euler_Kontrol, results_Gyro_Z, results_conn)
    
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    



    


if __name__ == "__main__":
    M2GR_main()
