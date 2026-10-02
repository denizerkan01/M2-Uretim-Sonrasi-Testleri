import time
import math
import general_functions as fnc
import M2GR_ResetTesti as M2GR_ResetTesti
import Role as Role
import numpy as np

def check_calibration_test(sensor_data, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value):

    result = {
        "reset_success": False,
        "accNorm": False,         
        "accNormValue": 0.0,      
        "accNormStatus": "fail",  
        "AccCalibrationSuccess": False,
        "CalibrationSuccess": False,
        "gyro_acilis_success": False,
        "acc_norm_gyro_success": False,
    }

    check_time_0 = M2GR_ResetTesti.check_reset_test(sensor_data)

    print("Reset Test Sonucu:",check_time_0)

    if not check_time_0.get("reset_success", False):
        return result

    result["reset_success"] = True

    #zero_rows_mat = np.where(sensor_data.time == 0)[0]

    #zero_rows = zero_rows_mat[0]

    acc_Norm = math.sqrt(
            sensor_data.accX[0] ** 2 + 
            sensor_data.accY[0] ** 2 + 
            sensor_data.accZ[0] ** 2
        )

    print("Acc Norm:",acc_Norm)

    result["accNormValue"] = acc_Norm

    if min_best_acc_norm_value <= acc_Norm <= max_best_acc_norm_value:
        result["accNorm"] = True
        result["accNormStatus"] = "best"
    elif min_ok_acc_norm_value <= acc_Norm <= max_ok_acc_norm_value:
        result["accNorm"] = True
        result["accNormStatus"] = "noted"
    else:
        result["accNorm"] = False
        result["accNormStatus"] = "fail"

    result["AccCalibrationSuccess"] = result["accNorm"]

    print("AccCalibrationSuccess:", result["AccCalibrationSuccess"])

    result["gyro_acilis_success"] = check_time_0["gyro_zero"]

    print("gyro_acilis_success", result["gyro_acilis_success"])

    result["CalibrationSuccess"] = result["AccCalibrationSuccess"] and result["reset_success"]
    print("AccCalibrationSuccess", result["AccCalibrationSuccess"])
    print("CalibrationSuccess:", result["CalibrationSuccess"])

    result["acc_norm_gyro_success"] = result["CalibrationSuccess"] and result["gyro_acilis_success"]
    print("acc_norm_gyro_success:", result["acc_norm_gyro_success"])
    
    return result

def test_calibration(dlg, device_sn, base_path, acc_acilis_successfull_needed, acilis_acc_folder, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value, sleep_time):

    all_calibration_results = []
    #
    all_accNormStatus_results = []
    
    successful_runs = 0

    while successful_runs < acc_acilis_successfull_needed:
        time.sleep(5)
        current_attempt = successful_runs + 1
            
        Role.Role()
        
        log_acc_acilis = fnc.auto_start(dlg, device_sn, base_path, acilis_acc_folder, sleep_time)
    

        try:
            sensor_data_acc_acilis = fnc.parse_log(log_acc_acilis)
        except (FileNotFoundError, ValueError) as e:
            return None

        results_acc_acilis = M2GR_ResetTesti.check_reset_test(sensor_data_acc_acilis)

        if results_acc_acilis is False:
            continue   
        
        results_calib_test = check_calibration_test(sensor_data_acc_acilis, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value)
        

        if not results_calib_test.get("CalibrationSuccess", False):
            continue
                    
        else:

            all_calibration_results.append(results_calib_test)
            all_accNormStatus_results.append(results_calib_test["accNormStatus"])
            successful_runs += 1

    stored_values = [res.get("accNormValue", 0.0) for res in all_calibration_results]
    
        
    if stored_values:
        max_val = max(stored_values)
        min_val = min(stored_values)
                
        print(f"Max Acc Norm Değeri: {max_val:.4f}")
        print(f"Min Acc Norm Değeri: {min_val:.4f}")

    CalibrationSuccess = all(item['CalibrationSuccess'] for item in all_calibration_results)
    gyro_acilis_success = all(item['gyro_acilis_success'] for item in all_calibration_results)
    AccCalibrationSuccess = all(item['AccCalibrationSuccess'] for item in all_calibration_results)

    return {
        "CalibrationSuccess": CalibrationSuccess,
        "gyro_acilis_success": gyro_acilis_success,
        "AccCalibrationSuccess": AccCalibrationSuccess,
        "all_calibration_results": all_calibration_results,
        "all_accNormStatus_results": all_accNormStatus_results,
        "max_acc_norm": max_val,
        "min_acc_norm": min_val,
        "stored_values": stored_values,
    }


        

def M2GR_AccNormGyroAcilisTesti(dlg, device_sn, base_path, acc_acilis_folder, acc_acilis_successfull_needed, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value, sleep_time):

    acilis_folder_acc = fnc.navigate_to_folder(dlg, device_sn, base_path, acc_acilis_folder)

    return test_calibration(dlg, device_sn, base_path, acc_acilis_successfull_needed, acilis_folder_acc, max_ok_acc_norm_value, min_ok_acc_norm_value, max_best_acc_norm_value, min_best_acc_norm_value, sleep_time)
