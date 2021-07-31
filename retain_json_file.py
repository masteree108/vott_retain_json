import os
import sys
import json
import enum
import threading
import queue
import numpy as np
import shutil
import operate_vott_id_json as OVIJ
import fps_judge as FJ
import log as PYM
from tkinter import *
from tkinter import messagebox
import tkinter.font as font
import pandas as pd
from time import sleep
# install module
#pip install openpyxl

class retain_json_file(threading.Thread):
# private
    __log_name = '< class retain_json_file>'
    __ovij_list = []
    __all_file_list = []
    __all_json_file_list = []
    __amount_of_ovij = 0
    __amount_of_other_source_ovij = 0
    __amount_of_not_specify_timestamp_ovij = 0
    __amount_of_empty_file_ovij = 0
    __file_path = ''
    __empty_file_ovij_list = []
    __other_source_ovij_list = []
    __not_specify_timestamp_ovij_list = []
    __video_path = ''
    __not_belong_here_folder_path = '/not_belong_here/'
    __not_specify_timestamp_folder_path = 'not_specify_timestamp/'
    __other_source_folder_path = 'other_source/'
    __empty_timestamp_folder_path = 'empty_timestamp/'
    __vott_set_fps = 0
    __CSM_exist = False
    __retain_file_name = ''
    __start_time = ''
    __end_time = ''

    def __check_json_file_name(self):
        # if file name is not equal xxxx...xxx-asset.json,it will kick out to list
        temp = []
        for file_name in self.__all_file_list:
            self.pym.PY_LOG(False, 'D', self.__log_name, "__check_file_name: " + file_name)
            root, extension = os.path.splitext(file_name)
            if extension == '.json':
                if file_name.find("-asset.json")!=-1:
                    temp.append(file_name)

        self.pym.PY_LOG(False, 'D', self.__log_name, "all file checked ok(drop out those not .json files) ")
        if len(temp) != 0: 
            self.__all_file_list = temp.copy()
            # print all filename in the list
            for i in self.__all_file_list:
                self.pym.PY_LOG(False, 'D', self.__log_name, i)
            return 0
        else:
            return -1


    def __list_all_file(self, path):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'msg(file_path): ' + path)
        self.__all_file_list = os.listdir(path)
        amount_of_file = len(self.__all_file_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount_of_file:%d' % amount_of_file)
        return self.__check_json_file_name()

    def __create_ovij_list(self):
        for i,jt in enumerate(self.__all_file_list):
            root, extension = os.path.splitext(jt)
            if extension == ".json":
                self.__all_json_file_list.append(jt)
                ovij = ''
                ovij = OVIJ.operate_vott_id_json()
                self.__ovij_list.append(ovij)

        self.__amount_of_ovij = len(self.__ovij_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step1: %d' % self.__amount_of_ovij)
        self.__amount_of_ovij = len(self.__all_json_file_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step2: %d' % self.__amount_of_ovij)

    def __sort_ovij_list(self):
        temp_no_sort = []
        temp_ovij_list = []
        for i in range(self.__amount_of_ovij):
            temp_no_sort.append(self.__ovij_list[i].get_timestamp())
            self.pym.PY_LOG(False, 'D', self.__log_name, 'timestamp without sort %s' % str(temp_no_sort[i]))
        temp_sort = temp_no_sort.copy()
        temp_sort.sort()

        for i in range(self.__amount_of_ovij):
            self.pym.PY_LOG(False, 'D', self.__log_name, 'timestamp with sort %s' % str(temp_sort[i]))
            
        
        find_index = np.array(temp_no_sort)

        # sort ovij_list
        for i, tps in enumerate(temp_sort):
            index = np.argwhere(find_index == tps)
            temp_ovij_list.append(self.__ovij_list[int(index)])

        self.__ovij_list = []
        self.__ovij_list = temp_ovij_list.copy()
        for i in range(self.__amount_of_ovij):
            self.pym.PY_LOG(False, 'D', self.__log_name, 'ovij_list with sort %s' % str(self.__ovij_list[i].get_timestamp()))

        
    def __create_not_belong_here_folder(self):
        if os.path.isdir(self.__not_belong_here_folder_path) != 0:
            # folder existed
            shutil.rmtree(self.__not_belong_here_folder_path)
        os.makedirs(self.__not_belong_here_folder_path)

    def __create_empty_timestamp_folder(self):
        des_path = self.__not_belong_here_folder_path + self.__empty_timestamp_folder_path
        os.makedirs(des_path)
        return des_path

    def __create_other_source_folder(self):
        des_path = self.__not_belong_here_folder_path + self.__other_source_folder_path
        os.makedirs(des_path)
        return des_path

    def __create_not_specify_timestamp_folder(self):
        des_path = self.__not_belong_here_folder_path + self.__not_specify_timestamp_folder_path
        os.makedirs(des_path)
        return des_path

    def __deal_with_json_file_path_command(self, msg):
        self.__file_path = msg[15:]
        if self.__list_all_file(self.__file_path) == 0:
            self. __notify_tool_display_json_file_exist()
            self.show_info_msg_on_toast(" 提醒", "載入josn完成,請按 run 繼續執行 ")
            self.pym.PY_LOG(False, 'D', self.__log_name, 'file_path:%s' % self.__file_path)
        else:
            self.__notify_tool_display_json_file_not_exist()
            self.show_info_msg_on_toast("error", "此資料夾沒有 *.json files")
            self.pym.PY_LOG(True, 'E', self.__log_name, 'There are no any *.json files')
            self.shut_down_log("over")

    def __find_timestamp_index_at_target_frame(self, index):
        first_timestamp = self.__ovij_list[index].get_timestamp()
        first_timestamp_sec = int(first_timestamp)
        diff = first_timestamp - first_timestamp_sec
        self.pym.PY_LOG(False, 'D', self.__log_name, 'target timestamp diff:%s' % diff)
        return index

    def __notify_tool_display_json_file_exist(self):
        msg = 'json_file_existed:'
        self.td_queue.put(msg)
   
    def __notify_tool_display_json_file_not_exist(self):
        msg = 'no_json_file:'
        self.td_queue.put(msg)

    def __notify_tool_display_to_exit_system(self):
        msg = 'can_exit:'
        self.td_queue.put(msg)

    def __notify_tool_display_process_file_not_exist(self):
        msg = 'file_not_exist:'
        self.td_queue.put(msg)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'there no any files in the folder')

    def __deal_with_empty_timestamp_files(self):
        empty_all_json_file_list = []
        empty_ovij_list = []
        self.__empty_file_ovij_list = []

        des_path = self.__create_empty_timestamp_folder()
        # read json data and fill into ovij_list[num]
        for i in range(len(self.__all_json_file_list)):
            file_path = self.__file_path + '/' + self.__all_json_file_list[i]
            root, extension = os.path.splitext(file_path)
            if extension == '.json':
                if self.__ovij_list[i].read_all_file_info(self.__file_path, self.__all_json_file_list[i]) == -1:
                    empty_all_json_file_list.append(self.__all_json_file_list[i])
                    empty_ovij_list.append(self.__ovij_list[i])
                    shutil.move(file_path, des_path)

        # check if those .json file are empty or not correct data format just removing form ovij_list
        for i,empty_ovij_name in enumerate(empty_ovij_list):
            self.__ovij_list.remove(empty_ovij_list[i])
            self.__empty_file_ovij_list.append(empty_ovij_list[i])

        for i,empty_json_name in enumerate(empty_all_json_file_list):
            self.__all_json_file_list.remove(empty_json_name)

        self.__amount_of_empty_file_ovij = len(self.__empty_file_ovij_list) 
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of empty file ovij: %d' % self.__amount_of_empty_file_ovij)

        self.__amount_of_ovij = len(self.__all_json_file_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step3: %d' % self.__amount_of_ovij)
        self.__amount_of_ovij = len(self.__ovij_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step4: %d\n' % self.__amount_of_ovij)


    def __deal_with_other_source_files(self):
        des_path = self.__create_other_source_folder()

        # move jsons file that not belong here(other video sources)
        self.__other_source_ovij_list = []
        self.pym.PY_LOG(False, 'D', self.__log_name, 'retain_file_name:%s' % self.__retain_file_name)

        remove_ovij_list = []
        remove_all_json_file_list = []
        for i,ovij in enumerate(self.__ovij_list):
            try:
                self.pym.PY_LOG(False, 'D', self.__log_name, 'index:%d' % i)
                self.pym.PY_LOG(False, 'D', self.__log_name, 'ovij-asset_id:%s' % ovij.get_asset_id())
                self.pym.PY_LOG(False, 'D', self.__log_name, 'ovij-path:%s' % ovij.get_asset_path())
                file_name = ovij.get_asset_id()  + '-asset.json'
                file_path = self.__file_path + '/' + file_name
                self.pym.PY_LOG(False, 'D', self.__log_name, 'file_path:%s' % file_path)
                root, extension = os.path.splitext(ovij.get_parent_name())
                #self.pym.PY_LOG(False, 'D', self.__log_name, 'parent_name:%s' % ovij.get_parent_name())
                self.pym.PY_LOG(False, 'D', self.__log_name, 'parent_name:%s without extension' % root)
                if root.find(self.__retain_file_name) == -1:
                    # save those file that not belong here for saving to excel
                    self.__other_source_ovij_list.append(ovij)
                    shutil.move(file_path, des_path)
                    remove_ovij_list.append(ovij)
                    remove_all_json_file_list.append(file_name)

            except:
                self.pym.PY_LOG(False, 'E', self.__log_name, 'this file cause tool happening error:%s' % ovij.get_asset_path())
                shutil.move(file_path, self.__not_belong_here_folder_path)
        
        self.__amount_of_other_source_ovij = len(self.__other_source_ovij_list) 
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of not belong here ovij: %d' % self.__amount_of_other_source_ovij)
        self.__amount_of_ovij = len(self.__all_json_file_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step5: %s' % str(self.__amount_of_ovij))
        self.__amount_of_ovij = len(self.__ovij_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step6: %s\n' % str(self.__amount_of_ovij))


        # remove those ovij that are not belong in ovij_list
        for i,remove_ovij in enumerate(remove_ovij_list):
            self.__ovij_list.remove(remove_ovij)
            
        for i,remove_json_name in enumerate(remove_all_json_file_list):
            self.__all_json_file_list.remove(remove_json_name)

        self.__amount_of_other_source_ovij = len(self.__other_source_ovij_list) 
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of other sources ovij: %d' % self.__amount_of_other_source_ovij)
        self.__amount_of_ovij = len(self.__all_json_file_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step7: %s' % str(self.__amount_of_ovij))
        self.__amount_of_ovij = len(self.__ovij_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step8: %s\n' % str(self.__amount_of_ovij))

    def __deal_with_not_specify_timestamp_files(self, fps):
        self.pym.PY_LOG(False, 'D', self.__log_name, '__deal_with_no_specify_timestamp_files')
        des_path = self.__create_not_specify_timestamp_folder()
        self.pym.PY_LOG(False, 'D', self.__log_name, 'des_path:%s' % des_path)
        self.__not_specify_timestamp_ovij_list = []
        remove_ovij_list = []
        remove_all_json_file_list = []

        for i,ovij in enumerate(self.__ovij_list):
            try:
                timestamp = ovij.get_timestamp() 
                file_name = ovij.get_asset_id()  + '-asset.json'
                file_path = self.__file_path + '/' + file_name
                self.pym.PY_LOG(False, 'D', self.__log_name, 'file_path:%s' % file_path)
                file_name = ovij.get_asset_id()  + '-asset.json'
                if timestamp < self.__start_time or timestamp >= self.__end_time: 
                    #if self.fj.is_our_goal_timestamp(fps, timestamp, self.__start_time, self.__end_time) == False:
                    self.__not_specify_timestamp_ovij_list.append(ovij)
                    shutil.move(file_path, des_path)
                    remove_ovij_list.append(ovij)
                    remove_all_json_file_list.append(file_name)
                    self.pym.PY_LOG(False, 'E', self.__log_name, 'this file is not speicfy timestamp%s' % file_name)
                    self.pym.PY_LOG(False, 'E', self.__log_name, 'timestamp%d' % timestamp)
                else:
                    self.pym.PY_LOG(False, 'E', self.__log_name, 'this file is speicfy timestamp%s' % file_name)
                    self.pym.PY_LOG(False, 'E', self.__log_name, 'timestamp%d' % timestamp)
            except:
                self.pym.PY_LOG(False, 'E', self.__log_name, 'this file cause tool happening error:%s' % file_name)
        
        # remove those ovij that are not belong in ovij_list
        for i,remove_ovij in enumerate(remove_ovij_list):
            self.__ovij_list.remove(remove_ovij)
            
        for i,remove_json_name in enumerate(remove_all_json_file_list):
            self.__all_json_file_list.remove(remove_json_name)

        self.__amount_of_not_specify_timestamp_ovij = len(self.__not_specify_timestamp_ovij_list) 
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of not specify timestamp ovij: %d' % self.__amount_of_not_specify_timestamp_ovij)
        self.__amount_of_ovij = len(self.__all_json_file_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step9: %s' % str(self.__amount_of_ovij))
        self.__amount_of_ovij = len(self.__ovij_list)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount of ovij-step10: %s\n' % str(self.__amount_of_ovij))


    def __deal_with_file_list(self):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'self.__file_path:%s' % self.__file_path)
        
        self.__not_belong_here_folder_path = self.__file_path + self.__not_belong_here_folder_path
        self.__create_not_belong_here_folder()

        self.__create_ovij_list()
        
        self.__deal_with_empty_timestamp_files()
        
        self.__deal_with_other_source_files()

        # sort ovij_list by timestamp
        self.__sort_ovij_list()

        time_diff = self.__start_time - self.__end_time
        if time_diff != 0:
            # run bleow function must after finished ovij sort
            pre_timestamp = self.__ovij_list[0].get_timestamp()
            cur_timestamp = self.__ovij_list[1].get_timestamp()
            fps = self.fj.judge_vott_set_fps(pre_timestamp, cur_timestamp)
            if self.fj.check_support_fps(fps) == True:
                self.pym.PY_LOG(False, 'D', self.__log_name, 'fps support')
                self.__deal_with_not_specify_timestamp_files(fps)
            else:
                self.pym.PY_LOG(False, 'E', self.__log_name, 'fps:%d not support on this tool' % fps)
                
        self.__save_result_to_excel()

        return True

    def __save_result_to_excel(self):
                    
        self.pym.PY_LOG(False, 'D', self.__log_name, 'create excel file')
        self.pym.PY_LOG(False, 'D', self.__log_name, '===== excel ovij_list(our goal timestamp): =====')
        list_id = []
        list_name = []
        timestamp = []
        for i,ovij in enumerate(self.__ovij_list):
            self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_id:%s' % ovij.get_asset_id())
            self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_name:%s' % ovij.get_asset_name())
            self.pym.PY_LOG(False, 'D', self.__log_name, 'timestamp:%d' % ovij.get_timestamp())

            list_id.append(ovij.get_asset_id()+'-asset.json')
            list_name.append(ovij.get_asset_name())
            timestamp.append(ovij.get_timestamp())
        
        retain_data = pd.DataFrame({'asset_id':list_id, 'asset_name':list_name,'timestamp':timestamp})

        if self.__amount_of_not_specify_timestamp_ovij != 0:
            self.pym.PY_LOG(False, 'D', self.__log_name, '===== excel not specify timestamp file: =====')
            list_id = []
            list_name = []
            timestamp = []
            for i,nsto in enumerate(self.__not_specify_timestamp_ovij_list):
                self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_id:%s' % nsto.get_asset_id())
                self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_name:%s' % nsto.get_asset_name())
                self.pym.PY_LOG(False, 'D', self.__log_name, 'timestamp:%d' % nsto.get_timestamp())

                list_id.append(nsto.get_asset_id()+'-asset.json')
                list_name.append(nsto.get_asset_name())
                timestamp.append(nsto.get_timestamp())

            nsto_data = pd.DataFrame({'asset_id':list_id, 'asset_name':list_name,'timestamp':timestamp})

        
        self.pym.PY_LOG(False, 'D', self.__log_name, '===== excel other source files: =====')
        list_id = []
        list_name = []
        timestamp = []
        for i,oso in enumerate(self.__other_source_ovij_list):
            self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_id:%s' % oso.get_asset_id())
            self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_name:%s' % oso.get_asset_name())
            self.pym.PY_LOG(False, 'D', self.__log_name, 'timestamp:%d' % oso.get_timestamp())

            list_id.append(oso.get_asset_id()+'-asset.json')
            list_name.append(oso.get_asset_name())
            timestamp.append(oso.get_timestamp())

        oso_data = pd.DataFrame({'asset_id':list_id, 'asset_name':list_name,'timestamp':timestamp})
        
        self.pym.PY_LOG(False, 'D', self.__log_name, '===== excel json content is empty file: =====')
        list_id = []
        list_name = []
        for i,empty_file in enumerate(self.__empty_file_ovij_list):
            self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_id:%s' % empty_file.get_asset_id())
            self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_name:%s' % empty_file.get_asset_name())

            list_id.append(empty_file.get_asset_id()+'-asset.json')
            list_name.append(empty_file.get_asset_name())

        empty_data = pd.DataFrame({'asset_id':list_id, 'asset_name':list_name})
        
        save_path = ''
        filename = "result.xlsx"
        save_path = self.__not_belong_here_folder_path + filename
        writer = pd.ExcelWriter(save_path)
        retain_data.to_excel(writer, index=False, sheet_name=self.__retain_file_name)
        if self.__amount_of_not_specify_timestamp_ovij != 0:
            nsto_data.to_excel(writer, index=False, sheet_name="not_specify_timestamp")
        oso_data.to_excel(writer, index=False, sheet_name="other_sources")
        empty_data.to_excel(writer, index=False, sheet_name="empty_timestamp_json")

        # set column width
        writer.sheets[self.__retain_file_name].column_dimensions['A'].width = 50
        writer.sheets[self.__retain_file_name].column_dimensions['B'].width = 50
        writer.sheets[self.__retain_file_name].column_dimensions['C'].width = 30

        if self.__amount_of_not_specify_timestamp_ovij != 0:
            writer.sheets['not_specify_timestamp'].column_dimensions['A'].width = 50
            writer.sheets['not_specify_timestamp'].column_dimensions['B'].width = 50
            writer.sheets['not_specify_timestamp'].column_dimensions['C'].width = 30

        writer.sheets['other_sources'].column_dimensions['A'].width = 50
        writer.sheets['other_sources'].column_dimensions['B'].width = 50
        writer.sheets['other_sources'].column_dimensions['C'].width = 30

        writer.sheets['empty_timestamp_json'].column_dimensions['A'].width = 50
        writer.sheets['empty_timestamp_json'].column_dimensions['B'].width = 50

        writer.save()

# public
    def __init__(self, fm_process_que, td_que):
        threading.Thread.__init__(self)
        self.fm_process_queue = fm_process_que
        self.td_queue = td_que
        self.pym = PYM.LOG(True)
        self.fj = FJ.fps_judge()
        self.pym.PY_LOG(False, 'D', self.__log_name, 'init')
	
    def __del__(self):
        #deconstructor
        self.shut_down_log("over")

    def FMP_main(self, msg):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'receive msg from queue: ' + msg)
        if msg[:15] == "json_file_path:":
            self.__deal_with_json_file_path_command(msg)
        elif msg.find('deal_with_json_files:')!=-1:
            # make sure file_process folder is existed
            
            # read end time
            end_time_index = msg.find('@t2') + 3
            self.__end_time = msg[end_time_index:]
            self.pym.PY_LOG(False, 'D', self.__log_name, 'end_time:%s' % self.__end_time)

            # read start time
            start_time_index = msg.find('@t1') + 3
            self.__start_time = msg[start_time_index:end_time_index-3]
            self.pym.PY_LOG(False, 'D', self.__log_name, 'start_time:%s' % self.__start_time)

            retain_file_name_index = msg.find(':') + 1
            self.__retain_file_name = msg[retain_file_name_index:start_time_index-3]
            self.pym.PY_LOG(False, 'D', self.__log_name, 'retain_file_name:%s' % self.__retain_file_name)
            
            self.__start_time = self.time_covert_to_sec_format(self.__start_time)
            self.__end_time  = self.time_covert_to_sec_format(self.__end_time)
            self.pym.PY_LOG(False, 'D', self.__log_name, 'start_time(sec):%d' % self.__start_time)
            self.pym.PY_LOG(False, 'D', self.__log_name, 'end_time(sec):%d' % self.__end_time)

            if os.path.isdir(self.__file_path) != 0:
                if self.__deal_with_file_list():
                    self.__notify_tool_display_to_exit_system()
                    self.pym.PY_LOG(False, 'D', self.__log_name, '!!---FINISHED THIS ROUND,WAIT FOR NEXT ROUND---!!\n\n\n\n\n')
            else:
                self.__notify_tool_display_process_file_not_exist()
                self.pym.PY_LOG(True, 'E', self.__log_name, 'There are no file_process folder!!')
                self.shut_down_log("over")

    def run(self):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'run')
        while True:
            msg = self.fm_process_queue.get()
            self.FMP_main(msg)
            if msg == 'over':
                break
        self.shut_down_log("RJF_rpocess_over")
    
    def time_covert_to_sec_format(self, val):
        time_sec = 0
        h,m,s = val.strip().split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)

    def shut_down_log(self, msg):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'amount_of_ovij:%d' % self.__amount_of_ovij)
        self.pym.PY_LOG(True, 'D', self.__log_name, msg)

        # delete all ovij_list's pym process
        if self.__amount_of_ovij != 0:
            for i,ovij in enumerate(self.__ovij_list):
                ovij.shut_down_log("%d pym over" %i) 

        if self.__amount_of_not_specify_timestamp_ovij !=0:
            for i,ovij in enumerate(self.__not_specify_timestamp_ovij_list):
                ovij.shut_down_log("%d pym over" %i) 

        if self.__amount_of_other_source_ovij != 0:
            for i,ovij in enumerate(self.__other_source_ovij_list):
                ovij.shut_down_log("%d pym over" %i) 

        if self.__amount_of_empty_file_ovij != 0:
            for i,ovij in enumerate(self.__empty_file_ovij_list):
                ovij.shut_down_log("%d pym over" %i)
        # delete fps_judge class pym process
        self.fj.shut_down_log("over")

    def show_error_msg_on_toast(self, title, msg):
        messagebox.showerror(title, msg)

    def show_info_msg_on_toast(self, title, msg):
        messagebox.showinfo(title, msg)



