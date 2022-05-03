import time
import os
import os.path as osp
from os.path import join as pjoin
from datetime import datetime
import shutil

import numpy as np
from lpf.utils import get_module_dpath
from lpf.models import LiawModel
from lpf.initializers import InitializerFactory as InitFac
from lpf.initializers import LiawInitializer

if __name__ == "__main__":

    dx = 0.1
    dt = 0.01
    width = 128
    height = 128
    thr = 0.5
    n_iters = 1000000
    shape = (width, height)
    
    # Define directories.    
    ladybird_type = "haxyridis"
    dpath_data = pjoin(get_module_dpath("data"), ladybird_type)
    dpath_template = pjoin(dpath_data, "template")
    
    str_now = datetime.now().strftime('%Y%m%d-%H%M%S')
    dpath_output = pjoin(osp.abspath("./output"), "single_%s"%(str_now))
    os.makedirs(dpath_output, exist_ok=True)
        
    print(__file__)
    fpath_src = pjoin(osp.dirname(__file__), osp.basename(__file__))
    fpath_dst = pjoin(dpath_output, osp.basename(__file__))
    shutil.copyfile(fpath_src, fpath_dst)

            
    # Define ladybird type and load the corresponding data.
    ladybird_type = "haxyridis"
    dpath_data = pjoin(get_module_dpath("data"), ladybird_type)
    dpath_template = pjoin(dpath_data, "template")
    
    fpath_template = pjoin(dpath_template, "ladybird.png")    
    fpath_mask = pjoin(dpath_template, "mask.png")

    n2v = {"fitness": 14.488964778357358, "u0": 2.0, "v0": 1.0, "Du": 0.0004999999999999999, "Dv": 0.07500000000000001, "ru": 0.17999999999999997, "rv": 0.08099695756142364, "k": 0.20000000000000004, "su": 0.001, "sv": 0.025000000000000005, "mu": 0.07999999999999999, "init-pts-0": ["40", "10"], "init-pts-1": ["40", "30"], "init-pts-2": ["40", "50"], "init-pts-3": ["40", "70"], "init-pts-4": ["40", "90"], "init-pts-5": ["50", "10"], "init-pts-6": ["50", "115"], "init-pts-7": ["62", "50"], "init-pts-8": ["50", "70"], "init-pts-9": ["50", "90"], "init-pts-10": ["12", "10"], "init-pts-11": ["60", "30"], "init-pts-12": ["60", "50"], "init-pts-13": ["60", "50"], "init-pts-14": ["50", "85"], "init-pts-15": ["99", "10"], "init-pts-16": ["70", "111"], "init-pts-17": ["70", "50"], "init-pts-18": ["70", "70"], "init-pts-19": ["70", "90"], "init-pts-20": ["0", "0"], "init-pts-21": ["0", "0"], "init-pts-22": ["0", "0"], "init-pts-23": ["0", "0"], "init-pts-24": ["0", "0"], "width": 128, "height": 128, "dt": 0.01, "dx": 0.1, "n_iters": 500000, "thr": 0.5, "initializer": "NoneType"}
    
    # Create initializer
    initializer = None
    
    if not initializer:
    
        num_init_pts = 0
        init_pts = {}
        for name, val in n2v.items():
            if "init-pts" in name:
                print(name, val)
                init_pts[name] = (int(val[0]), int(val[1]))
                num_init_pts += 1
        
        ir_init = np.zeros(num_init_pts, dtype=np.int32)
        ic_init = np.zeros(num_init_pts, dtype=np.int32)
        
        for i, (name, val) in enumerate(init_pts.items()):
            ir_init[i] = val[0]
            ic_init[i] = val[1]
        
        initializer = LiawInitializer(ir_init=ir_init, ic_init=ic_init)
    
    
    # Create a model.
    model = LiawModel(
         width=width,
         height=height,
         dx=dx,
         dt=dt,
         n_iters=n_iters,
         initializer=initializer,
         fpath_template=fpath_template,
         fpath_mask=fpath_mask
     )
    
    
    params = np.zeros((8,), dtype=np.float64)

    params[0] = n2v["Du"]
    params[1] = n2v["Dv"]
    params[2] = n2v["ru"]
    params[3] = n2v["rv"]
    params[4] = n2v["k"]
    params[5] = n2v["su"]
    params[6] = n2v["sv"]
    params[7] = n2v["mu"]
    u0 = n2v["u0"]
    v0 = n2v["v0"]

    
    model.solve([u0, v0], params=params,
                n_iters=n_iters,
                period_output=5000,
                dpath_images=dpath_output)
