import os
import tkinter as Tk
import tkinter.font as font
from tkinter import messagebox
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import filedialog       #獲取文件全路徑
import log as PYM
import threading
import time
import queue
import numpy as np
from PIL import Image
from skimage import transform,data
import platform
from pathlib import Path


class tool_display():

#private
    __log_name = '< class tool display>'
    __root = Tk.Tk()
    __canvas = 0
    __set_font = font.Font(name='TkCaptionFont', exists=True)
    __already_load = False
    __version = "v0.0.1"

    def __init_buttons(self):
        # quit button
        quit_btn = Tk.Button(master = self.__root, text = 'Quit', command = self.system_quit)
        quit_btn['font'] = self.__set_font
        #quit_btn.pack(side = Tk.BOTTOM)
        quit_btn.pack(side = Tk.RIGHT)
        
        # get *.json data path button
        # 設置按鈕，並給它openpicture 命令
        get_json_data_path_btn = Tk.Button(master = self.__root, text='選擇json file來源資料夾', command = self.load_json_file_path)
        get_json_data_path_btn['font'] = self.__set_font
        get_json_data_path_btn.pack(side = Tk.RIGHT)
        
        # run button
        self.__run_btn = Tk.Button(master = self.__root, text='run', command = self.run_retain_json)  #設置按鈕，並給它run命令
        self.__run_btn['font'] = self.__set_font
        self.__run_btn.pack(side = Tk.RIGHT)
     
    def __check_json_file_already_load(self):
        if self.__already_load == False:
            self.pym.PY_LOG(False, 'D', self.__log_name, 'json files has not been loaded')
            return True
        else:
            self.pym.PY_LOG(False, 'D', self.__log_name, 'json files already loaded')

            return False
#public
    def __init__(self, td_que, fm_process_que):
        
        self.__already_load = False
        self.__set_font.config(family='courier new', size=10)
        self.td_queue = td_que
        self.fm_process_queue = fm_process_que
        self.pym = PYM.LOG(True)
        matplotlib.use('TkAgg')
        
        os_name = self.which_os()
        self.pym.PY_LOG(False, 'D', self.__log_name, 'OS:' + '%s' % os_name)
        if os_name == 'Linux':
            #規定窗口大小
            self.__root.geometry('1200x200')
            self.__root.resizable(width = False, height = False)   # 固定长宽不可拉伸
            #self.__root.attributes('-zoomed', True)
        elif os_name == 'Windows':
            self.__root.geometry('1200x200')
            self.__root.resizable(width = False, height = False)   # 固定长宽不可拉伸
            #self.__root.state('zoomed')
            #self.__root.state('normal')

        self.__root.title("識別非此資料夾之json檔案"+ "__" + self.__version)
        self.figure, self.ax = plt.subplots(1, 1, figsize=(16, 8))
        self.pym.PY_LOG(False, 'D', self.__log_name, 'self.figure:' + '%s' % self.figure)

        #放置標籤
        self.label_state = Tk.Label(self.__root,text = 'system state', image = None, font = self.__set_font)   #創建一個標籤
        self.label_state.pack()

        self.__init_buttons()
        self.__root.protocol("WM_DELETE_WINDOW", self.system_quit)

        # entry box
        self.entry_box_label = Tk.Label(self.__root, font=self.__set_font, text="輸入要保留的json資料影片名稱：").pack(side=Tk.LEFT)
        self.retain_file_name = Tk.Entry(self.__root, bd=2, font=self.__set_font)
        self.retain_file_name.pack(side=Tk.LEFT)
        self.retain_file_name.insert(0,"Drone_001")

        # entry box start time
        self.start_time_label = Tk.Label(self.__root, font=self.__set_font, text="start time:")
        self.start_time_label.place(width=150,height=30,x=10, y=30)
        self.entry_start_time = Tk.Entry(self.__root, bd=2, font=self.__set_font)
        self.entry_start_time.place(width=120,height=30,x=150, y=30)
        self.entry_start_time.insert(0,"00:00:00")
        
        # entry box end time
        self.end_time_label = Tk.Label(self.__root, font=self.__set_font, text="end time:")
        self.end_time_label.place(width=150,height=30,x=10, y=70)
        self.entry_end_time = Tk.Entry(self.__root, bd=2, font=self.__set_font)
        self.entry_end_time.place(width=120,height=30,x=150, y=70)
        self.entry_end_time.insert(0,"00:00:00")

    def __del__(self):               
        #deconstructor
        self.shut_down_log("over")

    def load_json_file_path(self):
        if self.__check_json_file_already_load() == True:
            file_path = filedialog.askdirectory()     #獲取*.json檔案資料夾路徑
            if os.path.isdir(file_path):
                self.pym.PY_LOG(False, 'D', self.__log_name, 'json file path:' + '%s' % file_path)
                self.fm_process_queue.put("json_file_path:" + str(file_path));
                msg = self.td_queue.get()

                if msg == 'no_json_file:':
                    self.__already_load = False
                elif msg == 'json_file_existed:':
                    self.label_state.config(text = 'json file path:' + file_path )
                    self.__already_load = True
            else:
                self.pym.PY_LOG(False, 'D', self.__log_name, 'json file path:' + '%s' % file_path + 'is not existed!!')
                self.__already_load = False
                self.label_state.config(text = 'json file path is not existed!!' )  
        else:
            self.show_info_msg_on_toast("提醒", "無法再次選擇 json file 路徑,請繼續執行 run 按鈕,或者關閉重開")

    def run_retain_json(self):
        if self.__already_load == True:
            if self.retain_file_name.get() != '':
                start_time = self.entry_start_time.get()
                end_time = self.entry_end_time.get()
                send_msg = 'deal_with_json_files:'+ self.retain_file_name.get() + '@t1'+ start_time + '@t2' + end_time
                self.fm_process_queue.put(send_msg)
                msg = self.td_queue.get()
                if msg == 'can_exit:':
                    self.show_info_msg_on_toast("提醒", "執行成功,詳細請參閱 ./not_belong_here/result.excel")
                    self.system_quit()
            else:
                self.show_info_msg_on_toast("提醒", "請填入json資料影片名稱,ex:Drone_001")

        else:
            self.show_info_msg_on_toast("提醒", "請先執行load josn file")

    
    def display_main_loop(self):
        Tk.mainloop()

    def shut_down_log(self, msg):
        self.pym.PY_LOG(True, 'D', self.__log_name, msg)

    #按鈕單擊事件處理函式
    def system_quit(self):
        #結束事件主迴圈，並銷燬應用程式視窗
        self.__root.quit()
        self.__root.destroy()
        self.shut_down_log("quit")

    def show_error_msg_on_toast(self, title, msg):
        messagebox.showerror(title, msg)

    def show_info_msg_on_toast(self, title, msg):
        messagebox.showinfo(title, msg)

    def show_warning_msg_on_toast(self, title, msg):
        messagebox.showwarinig(title, msg)

    def askokcancel_msg_on_toast(self, title, msg):
        return messagebox.askokcancel(title, msg)

    #定義並繫結鍵盤事件處理函式
    def on_key_event(self, event):
        print('you pressed %s'% event.key)
        key_press_handler(event, canvas, toolbar)
        canvas.mpl_connect('key_press_event', on_key_event)

    def which_os(self):
        os_name = platform.system()
        #if os_name == 'Linux':
        #elif os_name == 'Windows':
        return os_name

