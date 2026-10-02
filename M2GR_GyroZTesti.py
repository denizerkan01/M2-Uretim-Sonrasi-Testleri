import time
import numpy as np
import general_functions as fnc
import M2GR_ResetTesti as M2GR_ResetTesti
import Role as Role

def check_gyroz(sensor_data):

    result = {
                "reset_success": False, 
                "YawDiff": 0.0,      
                "GyroZSucess": False, 
            }

    check_time_0 = M2GR_ResetTesti.check_reset_test(sensor_data)
    
    if not check_time_0.get("reset_success", False):
        #print("Reset Testi: BAŞARISIZ!!! Gyro Z Testi Yapılamaz!")
        return result
        
    result["reset_success"] = True

    euler_data = np.degrees(sensor_data.eulerZ)

    first_euler = euler_data[0]
    last_euler = euler_data[-1]

    diff_first_last = abs(last_euler - first_euler)

    result["YawDiff"] = diff_first_last

    #print(first_euler)
    #print(last_euler)
    #print(diff_first_last)


    if diff_first_last > 0.3:
        result["GyroZSucess"] = False
        print("Test 6: \n Gyro Z Testi: \n Sonuç: BAŞARISIZ")
        #print("1 dakika içinde beklenen yaw farkı miktarı 0.3 derecedir. Bu testte yaw farkı:",diff_first_last)
    else:
        result["GyroZSucess"] = True
        print("Test 6: \n Gyro Z Testi: \n Sonuç: BAŞARILI")

    return result

def M2GR_GyroZTesti(dlg, device_sn, base_path, sub_folder, sleep_time_gyroz):
    
    time.sleep(1)
    print("Sistemi 1. Konuma Getirin")
    time.sleep(3)

    fnc.navigate_to_folder(dlg, device_sn, base_path, sub_folder)
    
    Role.Role()
                
    log_gyro_z_folder = fnc.auto_start(dlg, device_sn, base_path, sub_folder, sleep_time_gyroz)

    try:
        sensor_data_gyro_z = fnc.parse_log(log_gyro_z_folder)
    except (FileNotFoundError, ValueError) as e:
        #print(f"Parse edilemedi: {e}")
        return None
    
    result_gyroz = check_gyroz(sensor_data_gyro_z)

    return result_gyroz