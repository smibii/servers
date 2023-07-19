import TKinterModernThemes as TKMT
from TKinterModernThemes.WidgetFrame import Widget
from time import sleep
import tkinter as tk
import subprocess
import threading
import win32gui
import win32con
import json
import sys
import wmi
import os
import re

class App(TKMT.ThemedTKinterFrame):
    def __init__(self, theme, mode, usecommandlineargs=True, usethemeconfigfile=True):
        super().__init__(str("Server Manager"), theme, mode, usecommandlineargs, usethemeconfigfile)

        self.root.geometry("845x480")
        self.root.iconbitmap('assets\\favico.ico')
        self.root.protocol('WM_DELETE_WINDOW', self.stop)
      
        self.running_symbol = '❗'
        
        self.running_scripts = []
        self.update_running_scripts()
                
        self.Label(str("Server Manager"))
        
        self.servers_frame = self.addLabelFrame(str("Servers"))
        self.get_folders()
        self.safe_json()
            
        self.nextCol()
        self.Label('')
        self.actions_frame = self.addLabelFrame('Actions menu')
        
        self.start_button = self.actions_frame.ToggleButton(
            '     Start     ',
            tk.BooleanVar(value=True),
            self.start_scripts
        )
        self.start_button_data = {
            "disabled": False
        }
        
        self.kill_button = self.actions_frame.ToggleButton(
            '       Kill       ',
            tk.BooleanVar(),
            self.kill_scripts,
            col=2
        )
        self.kill_button_data = {
            "disabled": True
        }
        
        # self.open_button = self.actions_frame.ToggleButton(
        #     'Open Dir',
        #     tk.BooleanVar(),
        #     self.open_scripts,
        #     col=2
        # )
        # self.open_button_data = {
        #     "disabled": True
        # }
        
        self.actions_frame.AccentButton(
            '     Update     ',
            self.restart
        )
        self.actions_frame.AccentButton(
            '     Stop     ',
            self.stop,
            col=2
        )
        
        self.debugPrint()
        self.run_update = True
        self.start_thread(self.update_buttons)
        self.run()
        
    def restart(self):
        os.system('start /min Server.bat')
        self.run_update = False
        sleep(.5)
        exit()
        
    def stop(self):
        self.run_update = False
        self.root.destroy()
        sleep(.5)
        exit()
        
    def get_folders(self):
        self.boxes = []
        self.folders_json = json.load(open('folders.json', "r"))
        self.current_directory = os.getcwd()
        self.folders = [
            {
                "name": "All",
                "checked": True if self.folders_json[0]['checked'] else False,
                "jar": None
            },
            {
                "name": "Tcp",
                "checked": True if self.folders_json[1]['checked'] else False,
                "jar": None
            }
        ]
        self.all_servers_switch = self.servers_frame.SlideSwitch(
            'All',
            tk.BooleanVar(value=True) if self.folders[0]['checked'] else tk.BooleanVar(),
            self.toggle_checked, (0,)
        )
        for name in os.listdir(self.current_directory):
            if os.path.isdir(os.path.join(self.current_directory, name)) and name != 'Bungee' and name != 'modules':
                for file in os.listdir(self.current_directory + '/' + name):
                    if re.match(r'^.+\.jar', file):
                        if len(self.folders_json) > 0:
                            for folder in self.folders_json:
                                if folder['name'] == name:
                                    self.folders.append(folder)
                                    break
                                elif self.folders_json.index(folder) == len(self.folders_json) - 1:
                                    self.folders.append({
                                        "name": name,
                                        "checked": True,
                                        "jar": file
                                    })    
                        else:
                            self.folders.append({
                                "name": name,
                                "checked": True,
                                "jar": file
                            })
        col = 1
        for i in range(len(self.folders)):
            folder = self.folders[i]
            name = folder['name']
            if name != 'All':
                if len(self.boxes)%5 == 0:
                    col += 1
                checkbox = self.servers_frame.ToggleButton(
                    name,
                    tk.BooleanVar(value=True) if folder['checked'] else tk.BooleanVar(),
                    self.toggle_checked, (i,),
                    col=col
                )
                self.boxes.append(checkbox)
        self.check_all()
                
    def toggle_checked(self, i):
        folder = self.folders[i]
        name = folder['name']
        checked = folder['checked']
        if checked:
            folder['checked'] = False
        else:
            folder['checked'] = True 
        if name == 'All':
            for box in self.boxes:
                i = self.boxes.index(box)+1
                self.folders[i]['checked'] = True if not checked else False
                box['variable'] = tk.BooleanVar(value=True) if not checked else tk.BooleanVar()
                print(self.folders[i]['checked'], self.folders[i]['name'])
        print(folder['checked'], folder['name'])
        self.safe_json()
        self.check_all()
            
    def check_all(self):
        checked = 0
        for folder in self.folders:
            if folder['name'] != 'All' and folder['checked']:
                checked+=1
        if checked == len(self.folders) - 1:
            self.all_servers_switch['variable'] = tk.BooleanVar(value=True)
            self.folders[0]['checked'] = True
        else:
            self.all_servers_switch['variable'] = tk.BooleanVar()
            self.folders[0]['checked'] = False
                
    def safe_json(self):
        with open('folders.json', 'w') as f:
            json.dump(self.folders, f)
        
    def start_scripts(self):
        self.update_running_scripts()
        if not self.start_button_data['disabled']:
            for folder in self.folders:
                name = folder['name']
                jar = folder['jar']
                if folder['checked'] and name != 'All':
                    if name not in self.running_scripts:
                        if name == "Tcp":
                            can_run = True
                            for p in self.running_scripts:
                                if 'tcp' in p.lower():
                                    can_run = False
                                    break
                            if can_run:
                                os.system('start /min tcp_connect.bat')
                        else:
                            os.system(f'start /min "" start_scripts.bat {name} {jar}')
                        print(f'Starting script: {name}')
                    else:
                        print(f'ERR! {name} already running!')
            self.start_button_data['disabled'] = True
        else:
            self.start_button['variable'] = tk.BooleanVar()
        
    def kill_scripts(self):
        self.update_running_scripts()
        if not self.kill_button_data['disabled']:
            for folder in self.folders:
                name = folder['name']
                if folder['checked'] :
                    if name == "Tcp":
                        can_run = False
                        for p in self.running_scripts:
                            if 'tcp' in p.lower():
                                can_run = True
                                break
                        if can_run:
                            self.kill_script(p)
                    elif name in self.running_scripts:
                        if name != 'All':
                            self.kill_script(name)
                    else:
                        print(f'ERR! {name} not running!')
            self.kill_button_data['disabled'] = True
        else:
            self.kill_button['variable'] = tk.BooleanVar()
        
    def kill_script(self, name):
        for p in self.running_scripts:
            if p == name:
                handle = win32gui.FindWindow(None, name)
                win32gui.SetForegroundWindow(handle)
                win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)
                print(f'Killing script: {name}')
                break
        
    def update_buttons(self):
        update_count = 0
        update_max = -1
        update_int = .2
        while update_count != update_max and self.run_update:
            self.update_running_scripts()
            checked_sum = 0
            checked_is_running = 0
            for folder in self.folders:
                name = folder['name']
                checked = folder['checked']
                i = self.folders.index(folder)-1
                box = self.boxes[i]
                if checked and name != 'All':
                    checked_sum+=1
                    if name == 'Tcp':
                        running = False
                        for script in self.running_scripts:
                            if script == 'Connecting to TCP server' or re.match(r'^[0-9]\.tcp\..+$', script):
                                running = True
                                box['text'] = f'{self.running_symbol}{name}'
                                checked_is_running+=1
                                break
                        if not running:
                            box['text'] = name
                    elif name in self.running_scripts:
                        box['text'] = f'{self.running_symbol}{name}'
                        checked_is_running+=1
                    else:
                        box['text'] = name
            if not checked_sum and not checked_is_running:
                self.start_button['variable'] = tk.BooleanVar()
                self.start_button_data['disabled'] = True
                self.kill_button['variable'] = tk.BooleanVar()
                self.kill_button_data['disabled'] = True
            else:
                if not checked_is_running:
                    self.start_button['variable'] = tk.BooleanVar(value=True)
                    self.start_button_data['disabled'] = False
                    self.kill_button['variable'] = tk.BooleanVar()
                    self.kill_button_data['disabled'] = True
                elif checked_sum > checked_is_running:
                    self.start_button['variable'] = tk.BooleanVar(value=True)
                    self.start_button_data['disabled'] = False
                    self.kill_button['variable'] = tk.BooleanVar(value=True)
                    self.kill_button_data['disabled'] = False
                else:
                    self.start_button['variable'] = tk.BooleanVar()
                    self.start_button_data['disabled'] = True
                    self.kill_button['variable'] = tk.BooleanVar(value=True)
                    self.kill_button_data['disabled'] = False
            update_count+=1
            sleep(update_int)
            
    def update_running_scripts(self):
        self.running_scripts = []
        win32gui.EnumWindows(self.enumWindowsProc, 0)
        return self.running_scripts
        
    def enumWindowsProc(self, hwnd, lParam):
        title = win32gui.GetWindowText(hwnd)
        if len(title) != 0:
            self.running_scripts.append(title)
            
    def start_thread(self, func, args=()):
        thread = threading.Thread(target=func, args=args)
        thread.start()

if __name__ == "__main__":
    App(str("sun-valley"), str("dark"))