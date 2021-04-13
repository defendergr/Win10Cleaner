import tkinter as tk
import tkinter.ttk as ttk
import os
from tkinter import simpledialog
import shutil
import winreg
import subprocess
import threading
import time
import ctypes
import enum
import sys

class Cleaner():
    def __init__(self, root):
        '''window & app settings'''
        self.root = root
        root.title("Win 10 Cleaner")
        root.resizable(False, False)
        self.widgets()
        win_width = root.winfo_reqwidth()
        win_hight = root.winfo_reqheight()
        pos_right = int(root.winfo_screenwidth() / 3 - win_width / 3)
        pos_down = int(root.winfo_screenheight() / 3 - win_hight / 3)
        root.geometry("800x450+{}+{}".format(pos_right, pos_down))
        root.iconbitmap("icon.ico")
        self.freeDiskBefore=''
        self.freeDiskAfter=''
        self.progress = True
        self.psStatus = ''
        self.debug=0

    def widgets(self):
        '''main window widgets'''
        self.text = 'Win 10 Cleaner'
        self.bt_text = 'Εκκίνηση'
        self.font = 'Arial 15 bold'
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=1, fill='both')
        self.canvas = tk.Canvas(self.frame, bg='gray')
        self.canvas.pack(expand=1, fill='both')
        #dimiourgia antikimenon ston camva
        self.image_bg = tk.PhotoImage(file='image.gif')
        self.canvas.create_image(0, 0, image=self.image_bg, anchor='nw')
        self.pg_bar = ttk.Progressbar(self.canvas, orient = 'horizontal', length = 500, mode = 'determinate')
        self.pg_bar.pack()
        self.button1 = tk.Button(self.canvas, text=self.bt_text, font='Arial 12', command=self.start, width=15, anchor='s') #self.clean
        self.button1.pack()
        self.button2 = tk.Button(self.canvas, text='Έξοδος', font='Arial 12', command=self.root.destroy, width=10, anchor='s')
        self.button2.pack()
        self.buttoni = tk.Button(self.canvas, text='About', font='Arial 8 bold', width=6, command=self.info, anchor='s')
        self.buttoni.pack()
        #topothetish antikimenon ston camva
        self.pos_text = self.canvas.create_text(400, 150, text=self.text, font=self.font, width=400, anchor='n', fill='black')
        self.pos_pg_bar = self.canvas.create_window(400, 250, anchor='s', window=self.pg_bar)
        self.pos_b1 = self.canvas.create_window(400,300, anchor='s', window=self.button1)
        self.pos_b2 = self.canvas.create_window(750, 400, anchor='se', window=self.button2)
        self.pos_bi = self.canvas.create_window(797, 3, anchor='ne', window=self.buttoni)

    def progressBar(self):
        '''creates progress bar'''
        if self.freeDiskBefore != '':
            self.canvas.delete(self.endMSG)
        self.pg_bar['value'] = 0
        self.canvas.itemconfigure(self.pos_pg_bar, state='normal')  # canvas.itemconfigure(id, state='hidden'/'normal')
        self.progress = True
        self.freeDiskBefore = ''
        self.freeDiskAfter = ''

    def refresh(self):
        '''refresh threads'''
        self.root.update()
        self.root.after(100, self.refresh)

    def start(self):
        '''starts cleaning threads'''
        self.button1['state'] = 'disabled'
        self.progressBar()
        self.disk_size()
        self.start1()
        self.start2()
        self.registryPaths()
        self.start3()
        while self.th.is_alive():
            if self.debug == 1: print("waiting...")
            time.sleep(1)
            self.refresh()
            if self.th.is_alive() != True:
                self.disk_size()
                self.endMessage()
                self.button1['state'] = 'normal'


    def endMessage(self):
        '''end message'''
        spacefree = abs(int(self.freeDiskBefore)-int(self.freeDiskAfter))
        endMSG = f'Ελευθερώθηκαν {spacefree} ΜΒ από τον δίσκο'
        self.canvas.itemconfigure(self.pos_pg_bar,state='hidden')#canvas.itemconfigure(id, state='hidden'/'normal')
        self.endMSG = self.canvas.create_text(400, 200, text=endMSG, font=self.font, width=400, anchor='n',fill='black')

    def start1(self):
        '''temporary folder files delete'''
        self.refresh()
        threading.Thread(target=self.temp, daemon=True).start()
        threading.Thread(target=self.progress_bar(os.listdir(os.environ['temp'])), daemon=True).start()

    def start2(self):
        '''windows temporary folder files delete'''
        self.refresh()
        threading.Thread(target=self.win_temp, daemon=True).start()
        threading.Thread(target=self.progress_bar(os.listdir(os.environ['Windir']+'\Temp')), daemon=True).start()

    def start3(self):
        '''starts proccess for windows clean manager'''
        self.refresh()
        if self.debug == 1: print('here runs on start 3 before process')
        self.th = threading.Thread(target=self.clean_manager, daemon=True)
        self.th.start()
        if self.debug == 1: print('here runs on start 3 after process')

    def info(self):
        '''info about app'''
        simpledialog.messagebox.showinfo('About', 'Win 10 Cleaner v2.1\nCredits: \nΚωνσταντίνος Καρακασίδης')

    def clean_manager(self):
        '''execute windows clean manager with setted atributes'''
        subprocess.run(["cleanmgr", "/sagerun:1929"])
        if self.debug == 1: print('complete')

    def registryPaths(self):
        '''adds registry key for use from clean_manager function'''
        regpath = [r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Active Setup Temp Folders',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\BranchCache',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Downloaded Program Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Internet Cache Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Memory Dump Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Old ChkDsk Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Previous Installations',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Recycle Bin',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Service Pack Cleanup',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Setup Log Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\System error memory dump files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\System error minidump files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Temporary Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Temporary Setup Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Thumbnail Cache',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Update Cleanup',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Upgrade Discarded Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\User file versions',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Defender',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Error Reporting Archive Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Error Reporting Queue Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Error Reporting System Archive Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Error Reporting System Queue Files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows ESD installation files',
                   r'Software\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches\Windows Upgrade Log Files']
        for key in regpath:
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key)
            key2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0,winreg.KEY_WRITE)
            winreg.SetValueEx(key2,'StateFlags1926',0,winreg.REG_DWORD,2)
            winreg.CloseKey(key2)


    def temp(self):
        '''deletes user temp files'''
        self.deleting = shutil.rmtree(os.environ['temp'],ignore_errors=True)
        self.progress = False

    def win_temp(self):
        '''deletes windows temp files'''
        self.progress = True
        self.deleting = shutil.rmtree(os.environ['Windir']+'\Temp', ignore_errors=True)
        self.progress = False

    def progress_bar(self,DIR):
        '''progress bar update of temp function'''
        if self.debug== 1:print(len(DIR))
        beforedelete=len(DIR)
        while self.progress==True:
            curentValue = len(DIR)
            value = (curentValue - beforedelete) * 100
            if beforedelete <20:
                self.pg_bar['value'] = 100
            self.pg_bar['value'] = 100-value
            time.sleep(0.1)
            if self.debug== 1:print(self.pg_bar['value'],'progress bar value')

    def disk_size(self):
        total, used, free = shutil.disk_usage("/")
        if self.freeDiskBefore == '':
            self.freeDiskBefore = f'{free // (2 ** 20)}'
        else:
            self.freeDiskAfter = f'{free // (2 ** 20)}'
        if self.debug == 1:
            print(f"Total: {total / (2 ** 20):.2f} MB")
            print(f"Used: {used / (2 ** 20):.2f} MB")
            print(f"Free: {free / (2 ** 20):.2f} MB")
            print(self.freeDiskBefore, 'Before MB')
            print(self.freeDiskAfter, 'After MB')



# ------------------------------MS code for admin privileges start------------------------------------------------------

class SW(enum.IntEnum):

    HIDE = 0
    MAXIMIZE = 3
    MINIMIZE = 6
    RESTORE = 9
    SHOW = 5
    SHOWDEFAULT = 10
    SHOWMAXIMIZED = 3
    SHOWMINIMIZED = 2
    SHOWMINNOACTIVE = 7
    SHOWNA = 8
    SHOWNOACTIVATE = 4
    SHOWNORMAL = 1


class ERROR(enum.IntEnum):

    ZERO = 0
    FILE_NOT_FOUND = 2
    PATH_NOT_FOUND = 3
    BAD_FORMAT = 11
    ACCESS_DENIED = 5
    ASSOC_INCOMPLETE = 27
    DDE_BUSY = 30
    DDE_FAIL = 29
    DDE_TIMEOUT = 28
    DLL_NOT_FOUND = 32
    NO_ASSOC = 31
    OOM = 8
    SHARE = 26


def bootstrap():
    if ctypes.windll.shell32.IsUserAnAdmin():
        root = tk.Tk()#apo edo ksekinaei to programa mou
        Cleaner(root)#apo edo ksekinaei to programa mou
        threading.Thread(target=root.mainloop(), daemon=True).start()#apo edo ksekinaei to programa mou
    else:
        hinstance = ctypes.windll.shell32.ShellExecuteW(
            None, 'runas', sys.executable, sys.argv[0], None, SW.SHOWNORMAL
        )
        if hinstance <= 32:
            raise RuntimeError(ERROR(hinstance))

# ------------------------------MS code for admin privileges end--------------------------------------------------------

if __name__ == '__main__':
    app = bootstrap()
