import time
import math
import numpy as np
import general_functions as fnc
import M2GR_ResetTesti as M2GR_ResetTesti
import Role as Role

def check_euler(max_roll_value, min_roll_value, max_pitch_value, min_pitch_value, sensor_data):

    result = {
            "reset_success": False,       
            "MaxRollValue": 0.0, 
            "MinRollValue": 0.0, 
            "MaxPitchValue": 0.0, 
            "MinPitchValue": 0.0,
            "RollMeanValue": 0.0, 
            "PitchMeanValue": 0.0,     
            "RollSuccess": False,
            "PitchSuccess": False, 
            "EulerSuccess": False,
        }

    check_time_0 = M2GR_ResetTesti.check_reset_test(sensor_data)

    if not check_time_0.get("reset_success", False):
        #print("Reset Testi: BAŞARISIZ!!! Euler Testi Yapılamaz!")
        return result
    
    result["reset_success"] = True

    roll_data = np.degrees(sensor_data.eulerX)
    pitch_data = np.degrees(sensor_data.eulerY)

    MinPitchValue = min(pitch_data)
    MaxPitchValue = max(pitch_data)
    MinRollValue = min(roll_data)
    MaxRollValue = max(roll_data)

    print("Min Pitch ",MinPitchValue)
    print("Max Pitch ", MaxPitchValue)
    print("Min Roll ", MinRollValue)
    print("Max Roll ", MaxRollValue)

    mean_roll = np.mean(roll_data)
    mean_pitch = np.mean(pitch_data)

    mean_roll = abs(mean_roll)

    print("Mean Roll ", mean_roll)
    print("Mean Pitch ", mean_pitch)

    result["RollMeanValue"] = mean_roll
    result["PitchMeanValue"] = mean_pitch


    if min_roll_value <= mean_roll <= max_roll_value:
        result["RollSuccess"] = True
        print(f"Max Roll Değeri: {MaxRollValue:.4f}")
        print(f"Min Roll Değeri: {MinRollValue:.4f}")

    if min_pitch_value <= mean_pitch <= max_pitch_value:
        result["PitchSuccess"] = True
        print(f"Max Pitch Değeri: {MaxPitchValue:.4f}")
        print(f"Min Pitch Değeri: {MinPitchValue:.4f}")

    result["EulerSuccess"] = result["RollSuccess"] and result["PitchSuccess"]

    return result

def M2GR_EulerKontrolTesti(dlg, device_sn, base_path, sub_folder, euler_kontrol_folder, max_roll_value, min_roll_value, max_pitch_value, min_pitch_value, sleep_time):

    result = {
                    "test_1": False,
                    "test_1_roll": 0.0,
                    "test_1_pitch": 0.0,
                    "test_2": False,
                    "test_2_roll": 0.0,
                    "test_2_pitch": 0.0,
                    "test_3": False,
                    "test_3_roll": 0.0,
                    "test_3_pitch": 0.0,
                    "EulerSuccess": False,
                }
    
    fnc.navigate_to_folder(dlg, device_sn, base_path, sub_folder)

    #Test - 1: 0 Derece Testi
    time.sleep(1)
    print("Sistemi 1. Konuma Getirin")
    time.sleep(3)

    Role.Role()
            
    log_euler_kontrol = fnc.auto_start(dlg, device_sn, base_path, euler_kontrol_folder, sleep_time)

    try:
        sensor_data_euler_kontrol = fnc.parse_log(log_euler_kontrol)
    except (FileNotFoundError, ValueError) as e:
        print(f"Parse edilemedi: {e}")
        return None

    #results_euler_reset = M2GR_ResetTesti.check_reset_test(sensor_data_euler_kontrol)

    result_euler_kontrol = check_euler(max_roll_value, min_roll_value, max_pitch_value, min_pitch_value, sensor_data_euler_kontrol)

    result["test_1_roll"] = result_euler_kontrol["RollMeanValue"]
    result["test_1_pitch"] = result_euler_kontrol["PitchMeanValue"]
        

    if result_euler_kontrol["EulerSuccess"] == True:
        print("Test 6: \n Sonuç: BAŞARILI")
        result["test_1"] = True

    else:
        print("Test 6: \n Sonuç: BAŞARISIZ!!!")
        print("Roll Testi Sonucu:", result_euler_kontrol["RollSuccess"])
        print("Pitch Testi Sonucu:", result_euler_kontrol["PitchSuccess"])
        result["test_1"] = False

    #Test - 2: 90 Derece Testi
    time.sleep(1)
    print("Sistemi 2. Konuma Getirin")
    time.sleep(3)

    Role.Role()
                
    log_euler_kontrol_t2 = fnc.auto_start(dlg, device_sn, base_path, euler_kontrol_folder, sleep_time)
    
    try:
        sensor_data_euler_kontrol_t2 = fnc.parse_log(log_euler_kontrol_t2)
    except (FileNotFoundError, ValueError) as e:
        #print(f"Parse edilemedi: {e}")
        return None

    #results_euler_reset_t2 = M2GR_ResetTesti.check_reset_test(sensor_data_euler_kontrol_t2)
    
    result_euler_kontrol_t2 = check_euler(max_roll_value+90, min_roll_value+90, max_pitch_value, min_pitch_value, sensor_data_euler_kontrol_t2)

    result["test_2_roll"] = result_euler_kontrol_t2["RollMeanValue"]
    result["test_2_pitch"] = result_euler_kontrol_t2["PitchMeanValue"]

    if result_euler_kontrol_t2["EulerSuccess"] == True:
        print("Test 6 - 2: \n Sonuç: BAŞARILI")
        result["test_2"] = True
    
    else:
        print("Test 6 - 2 : \n Sonuç: BAŞARISIZ!!!")
        print("Roll Testi Sonucu:", result_euler_kontrol_t2["RollSuccess"])
        print("Pitch Testi Sonucu:", result_euler_kontrol_t2["PitchSuccess"])
        result["test_3"] = False

    #Test - 3: 180 Derece Testi
    time.sleep(1)
    print("Sistemi 3. Konuma Getirin")
    time.sleep(3)
    
    Role.Role()
                    
    log_euler_kontrol_t3 = fnc.auto_start(dlg, device_sn, base_path, euler_kontrol_folder, sleep_time)
        
    try:
        sensor_data_euler_kontrol_t3 = fnc.parse_log(log_euler_kontrol_t3)
    except (FileNotFoundError, ValueError) as e:
        #print(f"Parse edilemedi: {e}")
        return None
    
    #results_euler_reset_t3 = M2GR_ResetTesti.check_reset_test(sensor_data_euler_kontrol_t3)
        
    result_euler_kontrol_t3 = check_euler(max_roll_value+180, min_roll_value+180, max_pitch_value, min_pitch_value, sensor_data_euler_kontrol_t3)

    result["test_3_roll"] = result_euler_kontrol_t3["RollMeanValue"]
    result["test_3_pitch"] = result_euler_kontrol_t3["PitchMeanValue"]

    print(result["test_3_roll"])
    print(result["test_3_pitch"])
    
    if result_euler_kontrol_t3["EulerSuccess"] == True:
        print("Test 6 - 3: \n Sonuç: BAŞARILI")
        result["test_3"] = True
        
    else:
        print("Test 6 - 3 : \n Sonuç: BAŞARISIZ!!!")
        print("Roll Testi Sonucu:", result_euler_kontrol_t3["RollSuccess"])
        print("Pitch Testi Sonucu:", result_euler_kontrol_t3["PitchSuccess"])
        result["test_3"] = False

    result["EulerSuccess"] = result["test_1"] and result["test_2"] and result["test_3"]

    return result