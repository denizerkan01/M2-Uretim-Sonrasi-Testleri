import time
import general_functions as fnc
import Role as Role

def check_data_select(file_path, expected_columns):

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            header_line = f.readline()
    except OSError as e:
        raise IOError(f"Data Select Testi: Dosya Açılamadı: {file_path}") from e

    if not header_line:
        raise ValueError(
            f"Data Select Testi: Dosya boş veya header okunamadı: {file_path}"
        )

    header_line = header_line.rstrip("\n").rstrip("\r")

    raw_tokens = header_line.split(",")
    found_columns = [tok.strip() for tok in raw_tokens]
    found_columns = [tok for tok in found_columns if tok]

    expected_set = set(expected_columns)
    found_set = set(found_columns)

    missing_columns = sorted(expected_set - found_set)
    unexpected_columns = sorted(found_set - expected_set)

    return {
        "found_columns": found_columns,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "is_valid": not missing_columns and not unexpected_columns,
    }

def DataSelectTest(dlg, device_sn, base_path, sub_folder,  expected_columns, sleep_time):

    fnc.navigate_to_folder(dlg, device_sn, base_path, sub_folder)

    time.sleep(2)
    
    Role.Role()

    log_data_select = fnc.auto_start(dlg, device_sn, base_path, sub_folder, sleep_time)

    results = check_data_select(log_data_select, expected_columns)

    return results