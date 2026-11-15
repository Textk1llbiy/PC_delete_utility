import os, shutil
import yaml 
import datetime, time
import schedule
from win11toast import toast
from system_tray import SystemTrayApp
import ctypes
import threading
from web_server import app as flask_app

# Files Variables
cwdir = os.path.dirname(os.path.abspath(__file__))
os.system('title PC Utilities') # Set the name of the terminal to "PC Utilities" for better aesthetics

# colors 

red = '\u001b[31m'
orange = '\x1b[38;5;166m'
white = '\u001b[0m'
purple = '\u001b[95m'
green = '\u001b[92m'

# ------

# Import main settings
with open(fr"{cwdir}\Weekly_info.yaml", "r") as file:
    try:
        Log_number = yaml.safe_load(file)   

    except yaml.YAMLError as e:
        print(e) 

def Formatt_Log_Text(Text_to_Format, color: int = "white"): # 1 = rosso, 2 = arancione, 3 = bianco, 4 = viola, 5 = verde
    if color == "red" or color == 1:
        print (red+f"[ [{datetime.datetime.now()}] - [{os .getlogin()}] ] --- {Text_to_Format}")
    elif color == "orange" or color == 2:
        print (orange+f"[ [{datetime.datetime.now()}] - [{os .getlogin()}] ] --- {Text_to_Format}")
    elif color == "white" or color == 3:
        print (white+f"[ [{datetime.datetime.now()}] - [{os .getlogin()}] ] --- {Text_to_Format}")
    elif color == "purple" or color == 4:
        print (purple+f"[ [{datetime.datetime.now()}] - [{os .getlogin()}] ] --- {Text_to_Format}")
    elif color == "green" or color == 5:
        print (green+f"[ [{datetime.datetime.now()}] - [{os .getlogin()}] ] --- {Text_to_Format}")

    # Save Into a Log File 
    with open(fr"{cwdir}\Logs\Log_File_{Log_number["log_number"]}.txt", "a") as f:
        f.write(f"[ [{datetime.datetime.now()}] - [{os .getlogin()}] ] --- {Text_to_Format} \n")

Formatt_Log_Text("starting Base Set-up ------------------------------", color = "white")

try:
    Formatt_Log_Text("Trying To Import Setting")
    with open(fr"{cwdir}\Setting.yaml", "r") as file:
        Settings = yaml.safe_load(file)   
    Formatt_Log_Text("Correctly importe Settings File.", color = 5)

except Exception as e:
    Formatt_Log_Text(f"There was a Fatal Error in trying to import the file Setting.yaml -- Error:{e}", color = 1)

# Hide console if setting is False
if Settings.get("Iconize_Console", True) == False:
    try:
        get_console_window = ctypes.windll.kernel32.GetConsoleWindow
        get_console_window.restype = ctypes.c_void_p
        get_console_window.argtypes = []
        hwnd = get_console_window()

        if hwnd:
            show_window = ctypes.windll.user32.ShowWindow
            show_window.argtypes = [ctypes.c_void_p, ctypes.c_int]
            show_window.restype = ctypes.c_int
            show_window(hwnd, 0)  # 0 = SW_HIDE
    except Exception as e:
        Formatt_Log_Text(f"Failed to hide console: {e}", color=2)

# ADD one to Log Variable
def Add_one_to_variable():
    Formatt_Log_Text("Trying To Modify The log Name File...")
    try:
        with open(fr"{cwdir}\Weekly_info.yaml") as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        Formatt_Log_Text("There Was a fatal Error in trying to modify the File called Weekly_info.yaml", color = 1)

    cfg["log_number"] += 1

    Formatt_Log_Text("Currently Saving Weekly_info.yaml")
    try:
        with open(fr"{cwdir}\Weekly_info.yaml", "w") as f:
            cfg = yaml.dump(
                cfg, stream=f, default_flow_style=False, sort_keys=False
            )
    except Exception as e:
        Formatt_Log_Text(f"There was a Fatal Error in trying to save the file Weekly_info.yaml -- Error:{e}", color = 1)      

    Formatt_Log_Text("Correcly Saved Weekly_info.yaml", color = 5)

Add_one_to_variable()

Formatt_Log_Text("Base set-uo Completed Starting Main Function ------", color = "white")

def start_web_server():
    """Start Flask web server in a separate thread"""
    flask_app.run(debug=False, port=5000, use_reloader=False)

def Add_deleted_Infos(how_much_deleted: float):
    with open(fr"{cwdir}\Weekly_info.yaml") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    cfg["how_much_weight_deleted"] += how_much_deleted

    with open(fr"{cwdir}\Weekly_info.yaml", "w") as f:
        cfg = yaml.dump(
            cfg, stream=f, default_flow_style=False, sort_keys=False
        )

def human_readable_weight(size, nd=2):
    for unit in ("B","KB","MB","GB","TB"):
        if size < 1024:
            return f"{size:.{nd}f} {unit}"
        size /= 1024

def Delete_Function(Files_to_delete):
    """
    Accepts either a dict (name: [path, bool]) or a list of [path, bool] pairs.
    Safely skips entries that are disabled or missing, and logs actions.
    """

    Weight_Cancelled: float = 0.0000
    entries = []
    if isinstance(Files_to_delete, dict):
        for name, val in Files_to_delete.items():
            try:
                path, enabled = val
            except Exception:
                continue
            entries.append((path, enabled))
    elif isinstance(Files_to_delete, (list, tuple)):
        for item in Files_to_delete:
            try:
                path, enabled = item
            except Exception:
                continue
            entries.append((path, enabled))
    else:
        Formatt_Log_Text('No valid entries to delete.')
        return

    for path, enabled in entries:
        if not enabled:
            continue
        if not os.path.exists(path):
            Formatt_Log_Text(f'Path not found: {path}', color = 2)
            continue
        try:
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        Data_weight = os.path.getsize(file_path)
                        Weight_Cancelled += Data_weight

                        os.remove(file_path)

                    elif os.path.isdir(file_path):
                        Dir_weight = os.path.getsize(file_path)
                        Weight_Cancelled += Dir_weight

                        shutil.rmtree(file_path)

                    Formatt_Log_Text(f'Deleted: {file_path}', color = 3)
                except Exception as e:
                    Formatt_Log_Text(f'Failed to delete {file_path}. Reason: {e}', color = 2)
        except Exception as e:
            Formatt_Log_Text(f'Failed to list directory {path}. Reason: {e}', color = 2)

    Formatt_Log_Text(f"Trying to Save Informations")
    try:
        Add_deleted_Infos(how_much_deleted = Weight_Cancelled)
        Formatt_Log_Text(f"Saved Informations!", color = 5)

    except Exception as e:
        Formatt_Log_Text(f"Error saving Informations. {e}", color = 1)

    with open(rf"{cwdir}\Weekly_info.yaml", "r") as file:
        deleted_weight = yaml.safe_load(file)
        
    Formatt_Log_Text("Formating Byte Size...")
    Formatt_Log_Text(f"Deleted Now: {human_readable_weight(Weight_Cancelled)}", color = 4)    
    Formatt_Log_Text(f"All Time Deleted: {human_readable_weight(deleted_weight['how_much_weight_deleted'])}", color = 4)
    Formatt_Log_Text("Finished Deleting Useless Files :D", color = 5)

    return Weight_Cancelled # Yea this Sucks Ass deam...

def main():
    print ("\n") #for clarity in the log file
    start = time.perf_counter()

    if Settings["Delete_Files"] == True:
        Weight_Cancelled = Delete_Function(Settings["Delete_specifics_dir"])
        if Settings["Window_Toast_Notification"] == True:
            toaster = toast()
            toaster.show_toast("Pc Utils", f"Finished Deleting Files, Amount: {human_readable_weight(Weight_Cancelled)}", duration=3)
        else:
            Formatt_Log_Text("Skipping Windows Toast Notification", color = 4)

    if Settings["Rotate_logs"] == True:
        Formatt_Log_Text("Trying to Rotate Logs...")
        try:
            for files in os.listdir(fr"{cwdir}\Logs"):
                file_path = os.path.join(fr"{cwdir}\Logs", files)
                if os.path.isfile(file_path):
                    file_creation_time = os.path.getctime(file_path)
                    file_age_days = (time.time() - file_creation_time) / (24 * 3600) # 24 * 3600 converts seconds to days

                    if file_age_days >= Settings["Log_Rotation"]["Log_File_days_to_keep"]:
                        os.remove(file_path)
                        Formatt_Log_Text(f"Deleted Log File: {file_path} after {file_age_days:.2f} days. Due to Rotation", color = 3)
            Formatt_Log_Text("Rotated Logs!", color = 5)

        except Exception as e:
            Formatt_Log_Text(f"There was a Fatal Error in trying to Rotate the Logs. {e}", color = 1)

    end = time.perf_counter()
    
    Formatt_Log_Text(f"Task Succesfully Completed in {end - start}", color = 4)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        Formatt_Log_Text(f"There was a Fatal Error it is Best to close the Program. {e}", color=1)
    
    # Import get_stats from system_tray for the callback
    from system_tray import get_stats

    # Create and start system tray app
    Formatt_Log_Text("Starting System Tray App...", color = 5)
    tray_app = SystemTrayApp(cwdir, main, lambda: get_stats(cwdir))
    tray_app.start_tray()
    Formatt_Log_Text("System Tray App Started - Check system tray icon", color = 5)
    
    # Start web server in a separate thread
    Formatt_Log_Text("Starting Web Dashboard Server...", color = 5)
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    Formatt_Log_Text("Web Dashboard started at http://localhost:5000", color = 5)

    schedule.every(Settings["Hours_Between_Executing"]).hours.do(main)

    # Keep the program running to allow scheduled tasks to execute
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        Formatt_Log_Text("Program interrupted by user", color = 5)
    except SystemExit:
        pass
    finally:
        Formatt_Log_Text("Exiting PC Utils...", color = 5)
