import os
import sys
import log as PYM
from _pydecimal import Decimal, Context, ROUND_HALF_UP
import numpy as np

class fps_judge():
# private
    # unit: second ,DP=Decimal point
    __frame_timestamp_DP_15fps = [0, 0.066667, 0.133333, 0.2, 0.266667, 0.333333,
                       0.4, 0.466667, 0.533333, 0.6, 0.666667, 0.733333,
                       0.8, 0.866667, 0.933333]

    __format_15fps = ['mp4', '066667', '133333', '2', '266667', '333333',
                       '4', '466667', '533333', '6', '666667', '733333',
                       '8', '866667', '933333']

    # if there is needing another format fps please adding here

    __frame_timestamp_DP_6fps = [0, 0.166667, 0.333333, 0.5, 0.666667, 0.833333]
    __format_6fps = ['mp4', '166667', '333333', '5', '666667', '833333']

    __frame_timestamp_DP_5fps = [0, 0.2, 0.4, 0.6, 0.8]
    __format_5fps = ['mp4', '2', '4', '6', '8']

    '''
        pick up frame description:
        if source_video_fps = 29,
        (1) setted project frame rate = 29, pick up 29 frames(1sec)
            pick_up_frame_interval = 1
            loop_counter(start number is 0)
            pick up frame:  | judgement:   
            0               | == 1-1 (pick_up_interval -1)
            1               | == 2-1 
            2               | == 3-1
            ...
            28              | == 29-1

        (2) setted project frame rate = 15, only pick 15 frames from 30 frames(1sec)
            pick_up_frame_interval = round(29/15) = 2
            loop_counter(start number is 0)
            pick up frame:  | judgement:   
            1               | == 2-1 (pick_up_interval -1)
            3               | == 4-1 
            5               | == 6-1
            7               | == 8-1
            9               | == 10-1
            11              | == 12-1
            13              | == 14-1
            15              | == 16-1
            17              | == 18-1
            19              | == 20-1
            21              | == 22-1
            23              | == 24-1
            25              | == 26-1
            27              | == 28-1
            29              | == 30-1

        (3) setted project frame rate = 6, only pick 6 frames from 30 frames(1 sec)
            pick_up_frame_interval = round(29/6) = 5
            loop_counter(start number is 0)
            pick up frame:  | judgement:   
            4               | == 5-1 (pick_up_interval -1)
            9               | == 10-1 
            14              | == 15-1
            19              | == 20-1
            24              | == 25-1
            29              | == 30-1

        (4) setted project frame rate = 5, only pick 5 frames from 30 frames(1 sec)
            pick_up_frame_interval = round(29/5) = 6
            loop_counter(start number is 0)
            pick up frame:  | judgement:   
            5               | == 6-1 (pick_up_interval -1)
            11              | == 12-1 
            17              | == 18-1
            23              | == 24-1
            29              | == 30-1

    '''

    __vott_video_fps = 0
    
# public
    def __init__(self):
        self.pym = PYM.LOG(True) 
        self.__vott_video_fps = 6

    def __del__(self):
        #deconstructor
        self.shut_down_log("over")

    def judge_vott_set_fps(self, pre_timestamp, cur_timestamp):           
        vott_set_fps = 1 / (cur_timestamp - pre_timestamp)
        vott_set_fps = round(vott_set_fps, 1)                                                                                                                       
        self.pym.PY_LOG(False, 'D', self.__class__, 'vott_set_fps %s' % str(vott_set_fps))
        self.__vott_video_fps = vott_set_fps
        return vott_set_fps

    def shut_down_log(self, msg):
        self.pym.PY_LOG(True, 'D', self.__class__, msg)

    def check_support_fps(self, vott_video_fps):
        self.__vott_video_fps = vott_video_fps
        if vott_video_fps == 15:
            return True
        # for adding new fps format use, please write it here
        elif vott_video_fps == 6:
            return True
        elif vott_video_fps == 5:
            return True
        else:
            self.pym.PY_LOG(False, 'E', self.__class__, 'This version only could track 5 or 15 fps that user setting on the VoTT')
            return False


