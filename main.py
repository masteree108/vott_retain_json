import tkinter as Tk
import os              
import sys 
import matplotlib
import tool_display as TD
import retain_json_file as RJF
import log as PYM
import threading
import time
import queue


def close_all_process(pym, RJF_process_queue):
    pym.PY_LOG(True, 'D', py_name, "over")
    RJF_process_queue.put("over")


def main(td_queue, RJF_process_queue):
    # processing thread
    RJF_process.start()

    # tool display thread
    td.display_main_loop()

    # finished
    close_all_process(pym, RJF_process_queue)

if __name__ == '__main__':
    py_name = '< main >'

    td_queue = queue.Queue()
    RJF_process_queue = queue.Queue()

    # class init
    pym = PYM.LOG(True)
    pym.PY_LOG(False, 'D', py_name, '\n +++++++++++++++++++++++++++++++++ start init ++++++++++++++++++++++++++++++++++++')

    td = TD.tool_display(td_queue, RJF_process_queue)
    
    RJF_process = RJF.retain_json_file(RJF_process_queue, td_queue) 
    
    main(td_queue, RJF_process_queue)
