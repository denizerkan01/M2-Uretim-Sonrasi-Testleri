import time
import numpy as np
import serial.tools.list_ports
import general_functions as fnc
import M2GR_ResetTesti as M2GR_ResetTesti
import KalibrasyonKontrolTesti as KalibrasyonKontrolTesti
import Role as Role


def RS422_232Testi(dlg, file_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro, ref_matrix_magn, kalibrasyon_kontrol_folder):

    result = {  "result_422": False, 
                "result_232": False, 
                "result_conn": False, 

    }

    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    
    ports = list(serial.tools.list_ports.comports())
    target_enhanced = fnc.find_port("Enhanced", ports)
    target_standard = fnc.find_port("Standard", ports)

    
    if fnc.try_connect(dlg, target_enhanced, "Enhanced"):
        #results_422_conn = KalibrasyonKontrolTesti.KalibrasyonKontrolTesti(dlg,file_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro, ref_matrix_magn, kalibrasyon_kontrol_folder)       
        results_422_conn = KalibrasyonKontrolTesti.KalibrasyonKontrolTesti(dlg,file_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro, kalibrasyon_kontrol_folder)
        if results_422_conn["device_sn_match"] == True:
            result["result_422"] = True
        else:
            result["result_422"] = False


    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    
    if fnc.try_connect(dlg, target_standard, "Standard"):
        #results_232_conn = KalibrasyonKontrolTesti.KalibrasyonKontrolTesti(dlg,file_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro, ref_matrix_magn, kalibrasyon_kontrol_folder)
        results_232_conn = KalibrasyonKontrolTesti.KalibrasyonKontrolTesti(dlg,file_path, device_sn, hw_num, firmware_version, device_name, ref_matrix_acc, ref_matrix_gyro,  kalibrasyon_kontrol_folder)
        if results_232_conn["device_sn_match"] == True:
            result["result_232"] = True
        else:
            result["result_232"] = False

    result_conn = result["result_422"] and result["result_232"]

    if result_conn == True:
        print("Test 6: BAŞARILI")
        result["result_conn"] = True
    else:
        result["result_conn"] = False
        if result["result_422"] == False:
            print("UART ile Bağlanılamadı")
        if result["result_232"] == False:
            print("RS232 ile Bağlanılamadı")

    dlg.child_window(title="Disconnect", control_type="Button").click_input()

    return result