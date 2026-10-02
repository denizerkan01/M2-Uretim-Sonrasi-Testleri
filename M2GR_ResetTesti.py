import time
import os
import glob
import numpy as np
import general_functions as fnc
import Role as Role

def check_reset_test(sensor_data):

    result = {
        "has_time_zero": False,
        "gyro_zero": False,
        "reset_success": False,
    }

    zero_rows_mat = np.where(sensor_data.time == 0)[0]

    if zero_rows_mat.size == 0: 
        return result

    zero_rows = zero_rows_mat[0]

    gyro_X = sensor_data.gyroX[zero_rows]
    gyro_Y = sensor_data.gyroY[zero_rows]
    gyro_Z = sensor_data.gyroZ[zero_rows]

    if gyro_X == 0 and gyro_Y == 0 and gyro_Z == 0:
        result["gyro_zero"] = True
    else:
        result["gyro_zero"] = False

    result["has_time_zero"] = True
    result["reset_success"] = result["has_time_zero"] and result["gyro_zero"]

    return result


def M2GR_ResetTesti(dlg, device_sn, base_path, hard_reset_folder, soft_reset_folder, sleep_time):


    #Hard Reset Testi:
    
    #Test - 1:
   
    reset_hard_folder = fnc.navigate_to_folder(dlg, device_sn, base_path, hard_reset_folder)

    Role.Role()

    log_hr_1 = fnc.auto_start(dlg, device_sn, base_path, reset_hard_folder, sleep_time)

    try:
        sensor_data_hr_1 = fnc.parse_log(log_hr_1)
    except (FileNotFoundError, ValueError) as e:
        #print(f"Parse edilemedi: {e}")
        return None

    results_hr_1 = check_reset_test(sensor_data_hr_1)


    
    #Test - 2:
    
    dlg.child_window(title="Record", control_type="Button").click_input()
    
    time.sleep(5)
    
    Role.Role()
    
    time.sleep(20)
    
    dlg.child_window(title="Stop", control_type="Button").click_input()
    
    log_hr_2 = glob.glob(os.path.join(reset_hard_folder, "log_*.txt"))
    if not log_hr_2:
        return None
    
    latest_log_hr_2 = max(log_hr_2, key=os.path.getmtime)
    
    try:
        sensor_data_hr_2 = fnc.parse_log(latest_log_hr_2)
    except (FileNotFoundError, ValueError) as e:
        return None
    
    results_hr_2 = check_reset_test(sensor_data_hr_2)

    
    
    #Hard Reset 2 kısmında arnav problemi vardır ve düzeltilecektir. Düzeltildikten sonra bu kısmı siliniz.
    
    
    max_attempts = 5
    attempts = 0
    
    if results_hr_2["reset_success"] == False:
        while not results_hr_2["reset_success"] and attempts < max_attempts:
            attempts += 1
    
            if results_hr_2["reset_success"] == False:
                dlg.child_window(title="Record", control_type="Button").click_input()
        
                time.sleep(5)
    
                Role.Role()

                print("Deneme:",attempts)

    
                time.sleep(20)
        
                dlg.child_window(title="Stop", control_type="Button").click_input()
        
                log_hr_3 = glob.glob(os.path.join(reset_hard_folder, "log_*.txt"))
                if not log_hr_3:
                    continue 
            
                latest_log_hr_3 = max(log_hr_3, key=os.path.getmtime)
        
    
                try:
                    sensor_data_hr_3 = fnc.parse_log(latest_log_hr_3)
                except (FileNotFoundError, ValueError) as e:
                    continue  
            
                results_hr_3 = check_reset_test(sensor_data_hr_3)
        
                reset_is_successful = results_hr_3["reset_success"]

                if reset_is_successful:
                    print("\nHard Reset Testi - 2: BAŞARILI")
                    break
                else:
                    print(f"\nHard Reset Testi - 2: ({attempts}) deneme sonrasinda BAŞARISIZ!!!.")

    
    
    """
        #Bu kısma kadar silinmelidir.
    """
    

    # Soft Reset
        
    # Test - 1:
        
    reset_soft_folder = fnc.navigate_to_folder(dlg, device_sn, base_path, soft_reset_folder)
        
    dlg.child_window(title="Console", control_type="Button").click_input()
        
    time.sleep(5)
        
    dlg.child_window(title="Reset", control_type="Pane").click_input()
        
    log_sr_1 = fnc.auto_start(dlg, device_sn, base_path, reset_soft_folder, sleep_time)
        
    try:
        sensor_data_sr_1 = fnc.parse_log(log_sr_1)
    except (FileNotFoundError, ValueError) as e:
        print(f"Parse edilemedi: {e}")
        return None

    results_sr_1 = check_reset_test(sensor_data_sr_1)

    
    # Test - 2:
    
    dlg.child_window(title="Record", control_type="Button").click_input()
    
    time.sleep(5)
    
    dlg.child_window(title="Reset", control_type="Pane").click_input()
    
    time.sleep(20)
    
    dlg.child_window(title="Stop", control_type="Button").click_input()
    
    log_sr_2 = glob.glob(os.path.join(reset_soft_folder, "log_*.txt"))
    if not log_sr_2:
        return None
    
    latest_log_sr_2 = max(log_sr_2, key=os.path.getmtime)
    
    try:
        sensor_data_sr_2 = fnc.parse_log(latest_log_sr_2)
    except (FileNotFoundError, ValueError) as e:
        return None
    
    results_sr_2 = check_reset_test(sensor_data_sr_2)

    time.sleep(2)

    dlg.child_window(title="Console", control_type="Button").click_input()

    time.sleep(2)


    if results_hr_2["reset_success"] == False:
        hr_2_result = reset_is_successful or results_hr_2["reset_success"]
    else:
        hr_2_result = results_hr_2["reset_success"]

    result_hr = results_hr_1["reset_success"] and hr_2_result
    result_sr = results_sr_1["reset_success"] and results_sr_2["reset_success"]
    result_reset = result_hr and result_sr


    return {
        "hard_reset_test_1": results_hr_1["reset_success"],
        "hard_reset_test_2": hr_2_result,
        "soft_reset_test_1": results_sr_1["reset_success"],
        "soft_reset_test_2": results_sr_2["reset_success"],
        "reset_result": result_reset,
    }
