import time
import numpy as np
from pywinauto.keyboard import send_keys
import M2GR_ResetTesti as M2GR_ResetTesti
import general_functions as fnc
import Role as Role

def check_gps(sensor_data, low_rate_id):

    result = {
                "reset_success": False,
                "GPSSatSuccess" : False,      
                "GpsSuccess": False, 
                "AntennaNumber": 0.0,
                }

    check_time_0 = M2GR_ResetTesti.check_reset_test(sensor_data)

    if not check_time_0.get("reset_success", False):
        print("Reset Testi: BAŞARISIZ!!! GPS Testi Yapılamaz!")
        return result
            
    result["reset_success"] = True

    status_data = np.array(sensor_data.status)
    low_rateX = np.array(sensor_data.lowRateX)
    low_rateY = np.array(sensor_data.lowRateY)
    low_rateZ = np.array(sensor_data.lowRateZ)
    data_time = np.array(sensor_data.time)

    #matches = np.where(status_data == low_rate_id or status_data == 47)[0]
    matches = np.where((status_data == low_rate_id))[0]

    if matches.size == 0:
        print("Test 8: \n GPS Testi: \n Sonuç: BAŞARISIZ \n GPS Verisi Bulunmamaktadır")
        result["GPSSatSuccess"] = False
        return result  
    else:
        first_idx = matches[0]
        if first_idx == 0:
            result["GPSSatSuccess"] = False
            return result

    low_rateX = low_rateX[first_idx:-1]
    low_rateY = low_rateY[first_idx:-1]
    low_rateZ = low_rateZ[first_idx:-1]
    data_time = data_time[first_idx:-1]

    
    idx_lr = np.where(low_rateX == 2)[0][0] #GPS validity ID=2

    result_validity = low_rateY[idx_lr]

    low_rateX = low_rateX[-150:-1]
    data_time = data_time[-150:-1]
    low_rateY = low_rateY[-150:-1]
    low_rateZ = low_rateZ[-150:-1]

    idx_nos = np.where(low_rateX == 1)[0][0] #Number of Sats ID=1

    result["AntennaNumber"] = low_rateZ[idx_nos]

    if result_validity == 1 and low_rateZ[idx_nos] >= 15:
        print("Test 8: \n GPS Testi: \n Sonuç: BAŞARILI")
        result["GPSSatSuccess"] = True
        result["GpsSuccess"] = True
    else:
        print("Test 8: \n GPS Testi: \n Sonuç: BAŞARISIZ")
        print("GPS Validity:",result_validity)
        print("Uydu Sayısı:",low_rateZ[idx_nos])

    return result

def Anten_Testi(dlg, device_sn, base_path, sleep_time, low_rate_id, gps_folder):
    time.sleep(5)
    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    #dlg.scroll("down", "page", 1)
    settings = dlg.child_window(title="Settings", auto_id="DevSettings", control_type="Window")
    lst = settings.child_window(auto_id="listViewSettings", control_type="List")

    page_down = lst.child_window(auto_id="DownPageButton", control_type="Button")
    page_down.click_input()

    dlg.child_window(title="TypeInitYaw", control_type="ListItem").double_click_input()
    #dlg.print_control_identifiers(depth=4, filename="tree2.txt")

    dlg.child_window(auto_id="LabeledComboControl", control_type="Pane").click_input()
    dlg.child_window(title="By GNSS = 2", control_type="ListItem").click_input()

    dlg.child_window(title="OK", control_type="Button").click_input()
    dlg.child_window(title="Save", control_type="Pane").click_input()
    send_keys("%{F4}")

    gps_folder = fnc.navigate_to_folder(dlg, device_sn, base_path, gps_folder)

    Role.Role()

    log_gps_folder = fnc.auto_start(dlg, device_sn, base_path, gps_folder, sleep_time)

    try:
        sensor_data_gps = fnc.parse_log(log_gps_folder)
    except (FileNotFoundError, ValueError) as e:
        print(f"Parse edilemedi: {e}")
        return None


    result_gps = check_gps(sensor_data_gps, low_rate_id)

    print("GPS Result:",result_gps)

    return result_gps