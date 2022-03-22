import os
import time
import numpy as np
from epics import caget, caput


class AndorDetector():
    def __init__(self, save_path) -> None:
        self.prefix = "s8_andor3_gypsum:"
        self.save_path = save_path
        self.mode = None
        self.config = {}
        self.switch_mode(new_mode='standby')
        self.andor_id = 1
    
    def check_config(self):
        return True

    def switch_mode(self, new_mode='standby', sample_name='test', num_img=100,
                    exp_time=1.0, save_path=None, group_id=None):
        assert new_mode in ['software_trigger', 'fixed_number', 
                            'standby', 'one_image']
        self.mode = new_mode
        if new_mode == 'standby':
            config = {
                "cam1:Acquire": 0,
                "TIFF1:AutoSave": 0,
                "cam1:ImageMode": 1
            }
        elif new_mode in ['software_trigger', 'fixed_number', 'one_image']:
            if save_path is None:
                save_path = self.save_path
            new_path = os.path.join(save_path, "S%04d_" % group_id +\
                sample_name)

            # make sure no such folder exists to avoid overwriting
            idx = 0
            while os.path.isdir(new_path):
                new_path = os.path.join(save_path, "S%04d_" % group_id +\
                    sample_name + '_%03d' % idx)
                idx += 1

            if new_mode == 'one_image':
                num_img = 1
                auto_save = False
            else:
                auto_save = True

            config = {
                "cam1:ImageMode": 0,
                "cam1:NumImages": num_img,
                "cam1:AcquireTime": exp_time,
                "TIFF1:FileName": "S%04d_" % group_id + sample_name,
                "TIFF1:FilePath": new_path,
                "TIFF1:FileNumber": 1,
                "TIFF1:AutoSave": auto_save,
                "TIFF1:AutoIncrement": True,
                "TIFF1:FileTemplate": "%s%s_%4.4d.tif",
            }

            if new_mode == 'software_trigger':
                # software trig is 3
                config["cam1:TriggerMode"] = 3
            else:
                # 0 is internal mode
                config["cam1:TriggerMode"] = 0

        self.config.update(config)
        for key, val in config.items():
            self.put_pv(key, val)
        return
    
    def acquire(self):
        try:
            if self.mode == 'software_trig':
                self.put_pv("cam1:Acquire", 1, wait=False)
            elif self.mode == 'fixed_number':
                self.put_pv("cam1:Acquire", 1, wait=True)
            elif self.mode == 'one_image':
                self.put_pv("cam1:Acquire", 1, wait=True)
                x = self.get_pv("image1:ArrayData")[0:5529600]
                x = x.reshape(2560, 2160).astype(np.uint16)
                # self.switch_mode(new_mode='standby')
                return x
        except (KeyboardInterrupt, Exception):
            self.switch_mode('standby')

    def trigger_one_image(self):
        if self.mode != 'software_trigger':
            return
        curr_num = self.get_pv("NumImagesCounter_RBV")
        total_num = self.get_pv("NumImages_RBV")
        self.put_pv("cam1:SoftwareTrigger", 1, wait=True)
    
    def put_pv(self, key, val, wait=True, timeout=3600, **kwargs):
        pv = self.prefix + key
        caput(pv, val, wait=wait, timeout=timeout, **kwargs)

    def get_pv(self, key, **kwargs):
        pv = self.prefix + key
        return caget(pv, **kwargs)
    
    def get_optimal_exposure_time(self, target=30000, max_iter=10):
        t0, t1 = 0.005, 1.000

        idx = 0
        while True:
            idx += 1
            tm = (t0 + t1) / 2.0
            self.switch_mode(new_mode='one_image', exp_time=tm, group_id=999)
            max_val = np.max(self.acquire())
            if abs(max_val - target) / target < 0.10:
                break
            elif max_val > target:
                t1 = tm
            else:
                t0 = tm
            if idx > max_iter:
                break
        self.switch_mode(new_mode='standby')

        return (t0 + t1) / 2.0