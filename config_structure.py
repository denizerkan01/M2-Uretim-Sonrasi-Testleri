import time
from pywinauto.keyboard import send_keys

def open_data_select(dlg, checkbox_states):

    dlg.child_window(title="Data Select", control_type="Button").click_input()
    
    for name, desired in checkbox_states:
        checkbox = dlg.child_window(title=name, control_type="CheckBox")
        state = checkbox.get_toggle_state()
        if state != desired:
            checkbox.click_input()

    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()


def open_low_rate(dlg):

    dlg.child_window(title="Data Select", control_type="Button").click_input()
    dlg.child_window(title="Configure...", auto_id="btLowRateConfigure", control_type="Pane").click_input()
    dlg.child_window(title="Defaults", control_type="Pane").click_input()
    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()

def target_meas(dlg, checkbox_states_target_meas):

    dlg.child_window(title="Settings", control_type="Button").click_input()

    dlg.child_window(title="TargetMeas", control_type="ListItem").double_click_input()

    for name, desired in checkbox_states_target_meas:
        checkbox = dlg.child_window(title=name, control_type="CheckBox")
        state = checkbox.get_toggle_state()
        if state != desired:
            checkbox.click_input()

    dlg.child_window(title="OK", control_type="Button").click_input()

    dlg.child_window(title="Save", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")

def config_structure_data_select_s3a(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)

def config_structure_data_select_m2gr(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)

def config_structure_data_select_m2hdr(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)


def config_structure_data_select(dlg, checkbox_states, checkbox_states_target_meas):

    open_data_select(dlg, checkbox_states)
    #time.sleep(5)
    #open_low_rate(dlg)
    #time.sleep(5)
    #target_meas(dlg,checkbox_states_target_meas)

def config_structure_kalibrasyon_kontrol_s3a(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)

def config_structure_kalibrasyon_kontrol(dlg, checkbox_states, checkbox_states_target_meas):

    open_data_select(dlg, checkbox_states)
    time.sleep(5)
    target_meas(dlg,checkbox_states_target_meas)

def config_structure_reset_s3a(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)


def config_structure_reset(dlg, checkbox_states, checkbox_states_target_meas):

    open_data_select(dlg, checkbox_states)
    #time.sleep(5)
    #target_meas(dlg,checkbox_states_target_meas)

def config_structure_acc_norm_gyro_acilis_s3a(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)

def config_structure_acc_norm_gyro_acilis(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)
    #time.sleep(5)
    #target_meas(dlg,checkbox_states_target_meas)

def config_structure_gps_acilis(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)
    open_low_rate(dlg)
    #time.sleep(5)
    #target_meas(dlg,checkbox_states_target_meas)

def config_structure_acc_dondurme_s3a(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)

def config_structure_acc_dondurme(dlg, checkbox_states, checkbox_states_target_meas):

    open_data_select(dlg, checkbox_states)
    #time.sleep(5)
    #target_meas(dlg,checkbox_states_target_meas)

def config_structure_euler_kontrol_s3a(dlg, checkbox_states):

    open_data_select(dlg, checkbox_states)

def config_structure_euler_kontrol(dlg, checkbox_states, checkbox_states_target_meas):

    open_data_select(dlg, checkbox_states)
    #time.sleep(5)
    #target_meas(dlg,checkbox_states_target_meas)

def config_structure_gyroz_s3a(dlg, checkbox_states):
    
    open_data_select(dlg, checkbox_states)

def config_structure_gyroz(dlg, checkbox_states, checkbox_states_target_meas):
    
    open_data_select(dlg, checkbox_states)
    time.sleep(5)
    target_meas(dlg,checkbox_states_target_meas)

def config_structure_gps(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)
    time.sleep(5)
    open_low_rate(dlg)

def config_structure_gps_m2gr(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)
    time.sleep(5)
    open_low_rate(dlg)
    """
    dlg.child_window(title="Settings", control_type="Button").click_input()
    dlg.Window.child_window(auto_id="DownButton", control_type="Button").double_click_input() 
    dlg.Window.child_window(auto_id="DownButton", control_type="Button").double_click_input()
    dlg.child_window(title="TypeInitYaw", control_type="ListItem").double_click_input()
    dlg.child_window(auto_id="LabeledComboControl", control_type="Pane").click_input()
    dlg.child_window(title="By GNSS = 2", control_type="ListItem").click_input()
    dlg.child_window(title="OK", control_type="Button").click_input()
    dlg.child_window(title="Save", control_type="Pane").click_input()
    send_keys("%{F4}")"""

def config_structure_rtk(dlg, checkbox_states):
    #open_data_select(dlg, checkbox_states)
    #time.sleep(5)
    open_low_rate(dlg)
    time.sleep(5)
    dlg.child_window(title="Settings", control_type="Button").click_input()
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input() 
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input()
    dlg.child_window(title="TypeInitYaw", control_type="ListItem").double_click_input()
    dlg.child_window(auto_id="LabeledComboControl", control_type="Pane").click_input()
    #time.sleep(5)
    #dlg.print_control_identifiers(filename = "typeinittree.txt")
    dlg.child_window(title="By GNSS = 2", control_type="ListItem").click_input()
    dlg.child_window(title="OK", control_type="Button").click_input()
    dlg.child_window(title="Save", control_type="Pane").click_input()

    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input() 
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input()
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input() 
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input()
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input() 
    dlg.child_window(auto_id="DownButton", control_type="Button").double_click_input()
    dlg.child_window(title="Port Protocol Settings", control_type="ListItem").double_click_input()
    dlg.child_window(auto_id="LabeledComboControl", control_type="Pane").click_input()

    
    time.sleep(5)
    dlg.print_control_identifiers(filename = "porttree.txt")
    #send_keys("%{F4}")

def config_structure_magn(dlg, checkbox_states, checkbox_states_target_meas):
    open_data_select(dlg, checkbox_states)
    target_meas(dlg,checkbox_states_target_meas)

def config_structure_magn_s3a(dlg, checkbox_states):
    open_data_select(dlg, checkbox_states)