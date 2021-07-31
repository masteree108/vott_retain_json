import os
import json
import enum
import log as PYM

class BBOX_ITEM(enum.Enum):
    height = 0
    width = 1
    left = 2
    top = 3

class VIDEO_SIZE(enum.Enum):
    W = 0
    H = 1

class operate_vott_id_json():
# private
    __log_name = '< class operate_vott_id_json>'
    __asset_id = ''
    __asset_format = ''
    __asset_name = ''
    __asset_path = ''

    __timestamp = 0.01
    __object_num = 0
    __file_path = ''
    __parent_name = ''

    def __print_read_parameter_from_json(self, num):
        self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_id: %s' % self.__asset_id)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_format: %s' % self.__asset_format)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'asset_path: %s' % self.__asset_path)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'timestamp: %.5f' % self.__timestamp)
        self.pym.PY_LOG(False, 'D', self.__log_name, 'parent_name: %.5f' % self.__parent_name)
   
    
    def __read_data_from_id_json_file(self):
        try:
            with open(self.__file_path, 'r') as reader:
                self.pym.PY_LOG(False, 'D', self.__log_name, '%s open ok!' % self.__file_path)
                jf = json.loads(reader.read())

                self.__asset_id = jf['asset']['id']
                self.__asset_format = jf['asset']['format']
                self.__asset_name = jf['asset']['name']
                self.__asset_path = jf['asset']['path']
                #self.__video_size[VIDEO_SIZE.W.value] = jf['asset']['size']['width']
                #self.__video_size[VIDEO_SIZE.H.value] = jf['asset']['size']['height']
                self.__timestamp = jf['asset']['timestamp']
                #self.__parent_id = jf['asset']['parent']['id']
                self.__parent_name = jf['asset']['parent']['name']
                #self.__parent_path = jf['asset']['parent']['path']

                # using length of region to judge how many objects in this frame
                self.__object_num = len(jf['regions'])

                reader.close()

                #self.__print_read_parameter_from_json(self.__object_num)
            return 0
        except:
            reader.close()
            self.pym.PY_LOG(False, 'E', self.__log_name, '%s has wrong format!' % self.__file_path)
            return -1

# public
    def __init__(self):
        # below(True) = exports log.txt
        self.pym = PYM.LOG(True)
        
    def __del__(self):
        #deconstructor
        self.shut_down_log("over")
    
    def check_file_exist(self):
        if os.path.exists(self.__file_path):
            self.pym.PY_LOG(False, 'D', self.__log_name, '%s existed!' % self.__file_path)
            return True
        else:
            self.pym.PY_LOG(True, 'E', self.__log_name, '%s is not existed!' % self.__file_path)
            return False

    def read_all_file_info(self, path, data_name):
        self.__file_path = path + '/' + data_name
        self.pym.PY_LOG(False, 'D', self.__log_name, 'file_path:%s' % self.__file_path)
        return self.__read_data_from_id_json_file()

    def get_asset_id(self):
        return self.__asset_id
    
    def get_asset_name(self):
        return self.__asset_name

    def get_asset_format(self):
        return self.__asset_format
    
    def get_asset_path(self):
        return self.__asset_path

    def get_timestamp(self):
        return self.__timestamp

    def get_parent_name(self):
        return self.__parent_name

    def shut_down_log(self, msg):
        self.pym.PY_LOG(True, 'D', self.__log_name, msg)
    
    def get_object_number(self):
        return self.__object_num

