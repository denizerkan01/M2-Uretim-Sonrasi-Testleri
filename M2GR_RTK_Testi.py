import sys
import time
import numpy as np
from pywinauto.keyboard import send_keys
import M2GR_ResetTesti as M2GR_ResetTesti
import general_functions as fnc
import Role as Role
from pywinauto import Desktop
import serial.tools.list_ports

def check_rtk(sensor_data, low_rate_rtk_id):

    result = {
            "reset_success": False,       
            "RTKSucess": False, 
            "AnttenaNumber": 0.0,
            }
    
    check_time_0 = M2GR_ResetTesti.check_reset_test(sensor_data)

    if not check_time_0.get("has_time_zero", False):
        print("Reset Testi: BAŞARISIZ!!! RTK Testi Yapılamaz!")
        return result
                
    result["reset_success"] = True

    status_data = np.array(sensor_data.status)
    low_rateX = np.array(sensor_data.lowRateX)
    low_rateZ = np.array(sensor_data.lowRateZ)

    first_idx = np.where(status_data == low_rate_rtk_id)[0]

    print(first_idx)

    if first_idx.size == 0: 
        return result

    first_idx = first_idx[0]

    
    low_rateX = low_rateX[first_idx:-1]
    low_rateZ = low_rateZ[first_idx:-1]
    low_rateX = low_rateX[-150:-1]
    low_rateZ = low_rateZ[-150:-1]

    idx_nos = np.where(low_rateX == 1)[0][0]

    result["AnttenaNumber"] = low_rateZ[idx_nos]

    if first_idx > 0 and low_rateZ[idx_nos] >= 15:
        result["RTKSucess"] = True
    else:
        result["RTKSucess"] = False

    return result

def M2GR_RTK_Testi(dlg, device_sn, base_path, rtk_folder, sleep_time, low_rate_rtk_id):

    result = {
                "RTK_Port_1": False,
                "Antenna_1": 0.0,
                "RTK_Port_2": False,
                "Antenna_2": 0.0,
                "RTK_Success": False,

    }
    time.sleep(5)
    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    settings = dlg.child_window(title="Settings", auto_id="DevSettings", control_type="Window")

    lst = settings.child_window(auto_id="listViewSettings", control_type="List")

    page_down = lst.child_window(auto_id="DownPageButton", control_type="Button")
    page_down.click_input()

    dlg.child_window(title="Port Protocol Settings", control_type="Text").double_click_input()
    #lst.print_control_identifiers(depth=4, filename="tree5.txt")

    dd = dlg.child_window(title="Port Protocol Settings", control_type="Text")

    edit = dlg.child_window(title="Edit Values", auto_id="DevSettingsMultipleComboForm", control_type="Window")
    row = edit.child_window(auto_id="LabeledComboControl",control_type="Pane",found_index=1) 
    combo = row.child_window(control_type="ComboBox")
    combo.click_input()

    combo.child_window(title="GNSSAidInOut = 4", control_type="ListItem").click_input()
    time.sleep(1)
    edit.child_window(title="OK", control_type="Button").click_input()
    time.sleep(1)
    dlg.child_window(title="Save", control_type="Pane").click_input()
    time.sleep(1)
    send_keys("%{F4}")
    time.sleep(1)

    rtk_folder = fnc.navigate_to_folder(dlg, device_sn, base_path, rtk_folder)

    dlg.child_window(title="Console", control_type="Button").click_input()
            
    time.sleep(2)
            
    dlg.child_window(title="Reset", control_type="Pane").click_input()


    dlg.child_window(title="Console", control_type="Button").click_input()
    time.sleep(2)


    

    dlg.child_window(title="Device", control_type="MenuItem").click_input()
    time.sleep(2)
                

    ports = list(serial.tools.list_ports.comports())
            
    target_enhanced = fnc.find_port("Enhanced", ports)

    dlg.child_window(title="NTRIP Client", control_type="MenuItem", found_index=0).click_input()

    ntrip = Desktop(backend="uia").window(title="NTRIP Client", control_type="Window")
    ntrip.wait("visible", timeout=10)

    ntrip.child_window(title="Get Mount Points", control_type="Pane").click_input()

    port = ntrip.child_window(auto_id="cbSerialPort", control_type="ComboBox")
    port.select(target_enhanced)

    ntrip.child_window(title="Connect", auto_id="btConnect", control_type="Pane").click_input()

    time.sleep(1)
    send_keys("%{F4}")

    Role.Role()

    log_rtk_folder = fnc.auto_start(dlg, device_sn, base_path, rtk_folder, sleep_time)

    try:
        sensor_data_rtk = fnc.parse_log(log_rtk_folder)
    except (FileNotFoundError, ValueError) as e:
        print(f"Parse edilemedi: {e}")
        return None
    
    result_rtk_p1 = check_rtk(sensor_data_rtk, low_rate_rtk_id)

    print("GPS Result:",result_rtk_p1)
    
    result["RTK_Port_1"] = result_rtk_p1["RTKSucess"]
    result["Antenna_1"] = result_rtk_p1["AnttenaNumber"]

    dlg.child_window(title="Device", control_type="MenuItem").click_input()
    time.sleep(2)

    dlg.child_window(title="NTRIP Client", control_type="MenuItem", found_index=0).click_input()

    ntrip = Desktop(backend="uia").window(title="NTRIP Client", control_type="Window")
    ntrip.wait("visible", timeout=10)

    ntrip.child_window(title="Disconnect", auto_id="btDisconnect", control_type="Pane").click_input()

    time.sleep(1)
    send_keys("%{F4}")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    settings = dlg.child_window(title="Settings", auto_id="DevSettings", control_type="Window")
        
    lst = settings.child_window(auto_id="listViewSettings", control_type="List")
        
    page_down = lst.child_window(auto_id="DownPageButton", control_type="Button")
    page_down.click_input()
        
    dlg.child_window(title="Port Protocol Settings", control_type="Text").double_click_input()
        
    dd = dlg.child_window(title="Port Protocol Settings", control_type="Text")
        
    edit = dlg.child_window(title="Edit Values", auto_id="DevSettingsMultipleComboForm", control_type="Window")
    row = edit.child_window(auto_id="LabeledComboControl",control_type="Pane",found_index=1) 
    combo = row.child_window(control_type="ComboBox")
    combo.click_input()
    
    combo.child_window(title="ArNavInOut = 1", control_type="ListItem").click_input()
    
    edit.child_window(title="OK", control_type="Button").click_input()
    time.sleep(1)
    dlg.child_window(title="Save", control_type="Pane").click_input()
    time.sleep(1)
    send_keys("%{F4}")
    time.sleep(1)
    

    


    

    dlg.child_window(title="Console", control_type="Button").click_input()
                
    time.sleep(2)
                
    dlg.child_window(title="Reset", control_type="Pane").click_input()
    
    
    dlg.child_window(title="Console", control_type="Button").click_input()

    dlg.child_window(title="Disconnect", control_type="Button").click_input()

    
    #Role.Role()
    time.sleep(5)

    #Port 2

    ports = list(serial.tools.list_ports.comports())
    target_enhanced = fnc.find_port("Enhanced", ports)    
        
    if not fnc.try_connect(dlg, target_enhanced, "Enhanced"):
        sys.exit("!!! Can't Connect to the Device !!!")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    
    settings = dlg.child_window(title="Settings", auto_id="DevSettings", control_type="Window")
    
    lst = settings.child_window(auto_id="listViewSettings", control_type="List")
    
    page_down = lst.child_window(auto_id="DownPageButton", control_type="Button")
    page_down.click_input()
    
    dlg.child_window(title="Port Protocol Settings", control_type="Text").double_click_input()
    
    dd = dlg.child_window(title="Port Protocol Settings", control_type="Text")
    
    edit = dlg.child_window(title="Edit Values", auto_id="DevSettingsMultipleComboForm", control_type="Window")
    row = edit.child_window(auto_id="LabeledComboControl",control_type="Pane",found_index=0) 
    combo = row.child_window(control_type="ComboBox")
    combo.click_input()
    
    combo.child_window(title="GNSSAidInOut = 4", control_type="ListItem").click_input()
    edit.child_window(title="OK", control_type="Button").click_input()
    dlg.child_window(title="Save", control_type="Pane").click_input()
    send_keys("%{F4}")

    rtk_folder = fnc.navigate_to_folder(dlg, device_sn, base_path, rtk_folder)
    
    dlg.child_window(title="Console", control_type="Button").click_input()
                
    time.sleep(2)
                
    dlg.child_window(title="Reset", control_type="Pane").click_input()
    
    
    dlg.child_window(title="Console", control_type="Button").click_input()
    time.sleep(2)
    
    dlg.child_window(title="Device", control_type="MenuItem").click_input()
    time.sleep(2)
                    
    ports = list(serial.tools.list_ports.comports())
                
    target_standard = fnc.find_port("Standard", ports)

    dlg.child_window(title="NTRIP Client", control_type="MenuItem", found_index=0).click_input()
    
    ntrip = Desktop(backend="uia").window(title="NTRIP Client", control_type="Window")
    ntrip.wait("visible", timeout=10)
    
    ntrip.child_window(title="Get Mount Points", control_type="Pane").click_input()
    
    port = ntrip.child_window(auto_id="cbSerialPort", control_type="ComboBox")
    port.select(target_standard)
    
    ntrip.child_window(title="Connect", auto_id="btConnect", control_type="Pane").click_input()
    
    time.sleep(1)
    send_keys("%{F4}")
    
    Role.Role()
    
    log_rtk_folder = fnc.auto_start(dlg, device_sn, base_path, rtk_folder, sleep_time)
    
    try:
        sensor_data_rtk_2 = fnc.parse_log(log_rtk_folder)
    except (FileNotFoundError, ValueError) as e:
        print(f"Parse edilemedi: {e}")
        return None
        
    result_rtk_p2 = check_rtk(sensor_data_rtk_2, low_rate_rtk_id)

    print("GPS Result 2:",result_rtk_p2)
        
    result["RTK_Port_2"] = result_rtk_p2["RTKSucess"]
    result["Antenna_2"] = result_rtk_p2["AnttenaNumber"]

    dlg.child_window(title="Device", control_type="MenuItem").click_input()
    time.sleep(2)
    
    dlg.child_window(title="NTRIP Client", control_type="MenuItem", found_index=0).click_input()
    
    ntrip = Desktop(backend="uia").window(title="NTRIP Client", control_type="Window")
    ntrip.wait("visible", timeout=10)
    
    ntrip.child_window(title="Disconnect", auto_id="btDisconnect", control_type="Pane").click_input()
    
    time.sleep(1)
    send_keys("%{F4}")
    
    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    settings = dlg.child_window(title="Settings", auto_id="DevSettings", control_type="Window")
            
    lst = settings.child_window(auto_id="listViewSettings", control_type="List")
            
    page_down = lst.child_window(auto_id="DownPageButton", control_type="Button")
    page_down.click_input()
            
    dlg.child_window(title="Port Protocol Settings", control_type="Text").double_click_input()
            
    dd = dlg.child_window(title="Port Protocol Settings", control_type="Text")
            
    edit = dlg.child_window(title="Edit Values", auto_id="DevSettingsMultipleComboForm", control_type="Window")
    row = edit.child_window(auto_id="LabeledComboControl",control_type="Pane",found_index=0) 
    combo = row.child_window(control_type="ComboBox")
    combo.click_input()
        
    combo.child_window(title="ArNavInOut = 1", control_type="ListItem").click_input()
        
    edit.child_window(title="OK", control_type="Button").click_input()
    time.sleep(1)
    dlg.child_window(title="Save", control_type="Pane").click_input()
    time.sleep(1)
    send_keys("%{F4}")
    time.sleep(1)

    dlg.child_window(title="Console", control_type="Button").click_input()
                    
    time.sleep(2)
                    
    dlg.child_window(title="Reset", control_type="Pane").click_input()
        
        
    dlg.child_window(title="Console", control_type="Button").click_input()
    
    dlg.child_window(title="Disconnect", control_type="Button").click_input()

    result["RTK_Success"] = result["RTK_Port_1"] and result["RTK_Port_2"]

    return result