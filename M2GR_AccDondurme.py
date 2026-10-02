import time
import math
import numpy as np
import M2GR_ResetTesti as M2GR_ResetTesti
import general_functions as fnc
import Role as Role

def test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time):

    result = {
            "results_calib_reset_test": False,
            "result_acc_dondurme_X_1": False,
            "result_acc_dondurme_X_2": False,
            "result_acc_dondurme_Y_1": False,
            "result_acc_dondurme_Y_2": False,
            "result_acc_dondurme_Z_1": False,
            "result_acc_dondurme_Z_2": False,
        }

    Role.Role()

    log_acc_dondurme = fnc.auto_start(dlg, device_sn, base_path, acc_dondurme_folder,  sleep_time)

    try:
        sensor_data_acc_dondurme = fnc.parse_log(log_acc_dondurme)
    except (FileNotFoundError, ValueError) as e:
        #print(f"Parse edilemedi: {e}")
        return None

    reset_results_acc_dondurme = M2GR_ResetTesti.check_reset_test(sensor_data_acc_dondurme)

    accX = sensor_data_acc_dondurme.accX
    accY = sensor_data_acc_dondurme.accY
    accZ = sensor_data_acc_dondurme.accZ

    acc_Norm = np.sqrt(accX ** 2 + accY ** 2 + accZ ** 2)

    mean_accX = np.mean(accX)
    mean_accY = np.mean(accY)
    mean_accZ = np.mean(accZ)

    mean_acc_Norm = np.mean(acc_Norm)

    print(mean_accX) 
    print(mean_accY)
    print(mean_accZ)

    print(mean_acc_Norm)
    print(-mean_acc_Norm - tolerance_value)
    print( -mean_acc_Norm + tolerance_value)
    

    if -mean_acc_Norm - tolerance_value <= mean_accZ <= -mean_acc_Norm + tolerance_value and abs(mean_accY) <= tolerance_value2 and abs(mean_accX) <= tolerance_value2:
        print("Döndürme Testi Başarılı Acc Z:-9.80, Acc Y ve Acc Z: 0")
        result["result_acc_dondurme_Z_1"] = True
    elif -mean_acc_Norm - tolerance_value <= mean_accY <= -mean_acc_Norm + tolerance_value  and abs(mean_accZ) <= tolerance_value2 and abs(mean_accX) <= tolerance_value2:
        print("Döndürme Testi Başarılı Acc Y:9.80, Acc X ve Acc Z: 0")
        result["result_acc_dondurme_Y_1"] = True
    elif mean_acc_Norm - tolerance_value <= mean_accZ <= mean_acc_Norm + tolerance_value and abs(mean_accY) <= tolerance_value2 and abs(mean_accX) <= tolerance_value2:
        print("Döndürme Testi Başarılı Acc Z:-9.80, Acc Y ve Acc Z: 0")
        result["result_acc_dondurme_Z_2"] = True
    elif mean_acc_Norm - tolerance_value <= mean_accY <= mean_acc_Norm + tolerance_value  and abs(mean_accZ) <= tolerance_value2 and abs(mean_accX) <= tolerance_value2:
        print("Döndürme Testi Başarılı Acc Y:9.80, Acc X ve Acc Z: 0")
        result["result_acc_dondurme_Y_2"] = True
    elif -mean_acc_Norm - tolerance_value <= mean_accX <= -mean_acc_Norm + tolerance_value  and abs(mean_accZ) <= tolerance_value2 and abs(mean_accY) <= tolerance_value2:
        print("Döndürme Testi Başarılı Acc X:-9.80, Acc X ve Acc Z: 0")
        result["result_acc_dondurme_X_1"] = True
    elif mean_acc_Norm - tolerance_value <= mean_accX <= mean_acc_Norm + tolerance_value  and abs(mean_accZ) <= tolerance_value2 and abs(mean_accY) <= tolerance_value2:
        print("Döndürme Testi Başarılı Acc X:9.80, Acc X ve Acc Z: 0")
        result["result_acc_dondurme_X_2"] = True
    else:
        print("Test BAŞARISIZ")

    return result

def M2GR_AccDondurmeTesti(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time):

    result = {
                "test_1": False,
                "test_2": False,
                "test_3": False,
                "test_4": False,
                "test_5": False,
                "test_6": False,
                "AccDondurmeSuccess": False,
            }

    acc_dondurme_folder = fnc.navigate_to_folder(dlg, device_sn, base_path, acc_dondurme_folder)

    time.sleep(1)

    print("Sistemi 1. Konuma Getirin")
    time.sleep(3)
    result_1 = test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time)
    print("Result 1:", result_1)

    if result_1["result_acc_dondurme_Z_1"] == True:
        result["test_1"] = True
        print("Konum 1 +")
    else:
        result["test_1"] = False
        print("Konum 1 -")

    time.sleep(1)
    
    print("Sistemi 2. Konuma Getirin")
    time.sleep(3)
    result_2 = test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time)
    print("Result 2:", result_2)

    if result_2["result_acc_dondurme_Y_1"] == True:
        result["test_2"] = True
        print("Konum 2 +")
    else:
        result["test_2"] = False
        print("Konum 2 -")

    time.sleep(1)

    print("Sistemi 3. Konuma Getirin")
    time.sleep(3)
    result_3 = test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time)
    print("Result 3:", result_3)

    if result_3["result_acc_dondurme_Z_2"] == True:
        result["test_3"] = True
        print("Konum 3 +")
    else:
        result["test_3"] = False
        print("Konum 3 -")

    time.sleep(1)

    print("Sistemi 4. Konuma Getirin")
    time.sleep(3)
    result_4 = test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time)
    print("Result 4:", result_4)

    if result_4["result_acc_dondurme_Y_2"] == True:
        result["test_4"] = True
        print("Konum 4 +")
    else:
        result["test_4"] = False
        print("Konum 4 -")

    time.sleep(1)

    print("Sistemi 5. Konuma Getirin")
    time.sleep(3)
    result_5 = test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time)
    print("Result 5:", result_5)

    if result_5["result_acc_dondurme_X_1"] == True:
        result["test_5"] = True
        print("Konum 5 +")
    else:
        result["test_5"] = False
        print("Konum 5 -")

    time.sleep(1)

    print("Sistemi 6. Konuma Getirin")
    time.sleep(3)
    result_6 = test_dondurme(dlg, device_sn, base_path, acc_dondurme_folder, tolerance_value, tolerance_value2, sleep_time)
    print("Result 6:", result_6)

    if result_6["result_acc_dondurme_X_2"] == True:
        result["test_6"] = True
        print("Konum 6 +")
    else:
        result["test_6"] = False
        #print("Konum 6 -")

    result["AccDondurmeSuccess"] = result["test_1"] and result["test_2"] and result["test_3"] and result["test_4"] and result["test_5"] and result["test_6"] 

    return result