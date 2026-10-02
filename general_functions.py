import time
import os
import glob
import csv
from pathlib import Path
from pywinauto.keyboard import send_keys
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
import serial.tools.list_ports
from pywinauto.timings import TimeoutError as PWTimeoutError

def find_port(keyword, ports):
    return next((p.device for p in ports if keyword in p.description), None)

def try_connect(dlg, port, label):
    

    dlg.child_window(title="Connect", control_type="Button").wait("visible enabled").click_input()
    time.sleep(1)
    menu_item = dlg.child_window(title=port, control_type="MenuItem", found_index=0)
    menu_item.wait("visible enabled", timeout=5).click_input()

    try:
        dlg.wait("ready", timeout=5)
    except PWTimeoutError:
        pass
    time.sleep(0.5)

    title = dlg.window_text()
    return title != "ArView"


def connect_device(dlg):

    ports = list(serial.tools.list_ports.comports())

    target_enhanced = find_port("Enhanced", ports)
    target_standard = find_port("Standard", ports)

    if target_enhanced is None and target_standard is None:
        return False

    if target_enhanced and try_connect(dlg, target_enhanced, "Enhanced"):
        print("-- Enhanced Port ile bağlanildi.")
        return True

    if target_standard and try_connect(dlg, target_standard, "Standard"):
        print("-- Standard Port ile bağlanildi.")
        return True

    return False

def find_port_by_keywords(keywords, ports):

    for port in ports:
        description = port.description.lower()
        if any(kw.lower() in description for kwstr in keywords if (kw := kwstr)):
            return port.device
    return None

def uart_connect(dlg):
    ports = list(serial.tools.list_ports.comports())

    target_cp210x = find_port_by_keywords(["CP210x", "Silicon Labs"], ports)

    if target_cp210x and try_connect(dlg, target_cp210x, "CP210x"):
        print(f"-- CP210x Port ({target_cp210x}) ile bağlanıldı.")
        return True

def get_uart_port():

    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        desc = port.description
        # CP210x/Silicon Labs olacak AMMA CP2105 veya Dual OLMAYACAK
        if ("CP210" in desc or "Silicon Labs" in desc) and not ("Dual" in desc or "CP2105" in desc):
            return port.device  # "COM9" dönecek
            
    return None

def uart_connect(dlg):
    target_port = get_uart_port()

    dlg.child_window(title="Connect", control_type="Button").wait("visible enabled").click_input()
    menu_item = dlg.child_window(title=target_port, control_type="MenuItem", found_index=0)
    menu_item.wait("visible enabled", timeout=5).click_input()

def navigate_to_folder(dlg, device_name, base_path, sub_folder):


    dlg.child_window(title="Logs", control_type="Pane").click_input()
    dlg.child_window(title="Change", control_type="Pane").click_input()

    target_folder = os.path.join(base_path, device_name, sub_folder)

    send_keys("^l")            
    time.sleep(0.3)
    send_keys("^a{DEL}")       
    send_keys(target_folder, with_spaces=True)
    send_keys("{ENTER}")
    dlg.child_window(auto_id="1", control_type="Button").click_input()

    return target_folder

def get_dir_size(path_str):
    root = Path(path_str)
    return sum(f.stat().st_size for f in root.rglob('*') if f.is_file())

def auto_start(dlg, device_sn, base_path, sub_folder, sleep_time):
    
    dlg.child_window(title="Record", control_type="Button").click_input()

    target_folder = os.path.join(base_path, device_sn, sub_folder)

    log_file = glob.glob(os.path.join(target_folder, "log_*.txt"))

    if not log_file:
        print("Log dosyasi bulunamadi", log_file)
        return None

    latest_log = max(log_file, key=os.path.getmtime)

    file_size = get_dir_size(latest_log)

    while file_size == 0:

        try:
            fd = os.open(latest_log, os.O_RDONLY)
            try:
                file_size = os.fstat(fd).st_size
            finally:
                os.close(fd)
        except OSError:
            file_size = 0

        if file_size > 0:

            time.sleep(sleep_time)

            dlg.child_window(title="Stop", control_type="Button").click_input()

            break

    time.sleep(1)

    if file_size == 0:
        print("Test Failed: File size değişmemektedir.")
        return None
    
    return latest_log



def _to_attr_name(header: str) -> str:
    parts = header.strip().split()
    if not parts:
        return ""
    first = parts[0][0].lower() + parts[0][1:]
    rest = "".join(p[0].upper() + p[1:] for p in parts[1:])
    return first + rest


class SensorData:

    def __repr__(self):
        n = len(self.headers) if hasattr(self, "headers") else 0
        n_rows = len(getattr(self, _to_attr_name(self.headers[0]), [])) if n else 0
        return f"<SensorData: {n} columns, {n_rows} rows>"


def parse_log(filepath: str) -> SensorData:

    with open(filepath, newline="") as f:
        reader = csv.reader(f)
        raw_header = next(reader)
        headers = [h.strip() for h in raw_header]
        attr_names = [_to_attr_name(h) for h in headers]

        columns = {name: [] for name in attr_names}

        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                continue  # skip blank lines
            for name, cell in zip(attr_names, row):
                cell = cell.strip()
                try:
                    columns[name].append(float(cell))
                except ValueError:
                    columns[name].append(cell)

    data = SensorData()
    for name, values in columns.items():
        setattr(data, name, np.array(values))
    data.headers = headers
    return data


