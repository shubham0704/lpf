import os
from os.path import join as pjoin
from datetime import datetime
from collections.abc import Sequence

import yaml
import numpy as np
import pygmo as pg
from PIL import Image

from lpf.utils import get_module_dpath
from lpf.utils import get_hash_digest


class EvoSearch:
    def __init__(self,
                 config,
                 model,
                 converter,                 
                 targets,
                 objectives,
                 droot_output=None):
        
        # Load hyperparameters.
        self.config = config
        self.model = model
        self.converter = converter

        if isinstance(targets, Sequence) and len(targets) < 1:
            raise ValueError("targets should be a sequence, "\
                             "which must have at least one target.")

        self.targets = targets

        self.objectives = objectives

        self.bounds_min, self.bounds_max = self.model.get_param_bounds()
        self.len_dv = self.model.get_len_dv()
        
        # Create a cache using dict.
        self.cache = {}

        # Create output directories.
        str_now = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.dpath_output = pjoin(droot_output, "search_%s"%(str_now))        
        self.dpath_population = pjoin(self.dpath_output, "population")
        self.dpath_best = pjoin(self.dpath_output, "best")

        os.makedirs(self.dpath_output, exist_ok=True)
        os.makedirs(self.dpath_population, exist_ok=True)
        os.makedirs(self.dpath_best, exist_ok=True)        
        
        # Write the config file.
        fpath_config = pjoin(self.dpath_output, "config.yaml")
        with open(fpath_config, 'wt') as fout:
            yaml.dump(config, fout)

    def fitness(self, x):
        digest = get_hash_digest(x)

        if digest in self.cache:
            arr_color = self.cache[digest]
        else:
            x = x[None, :]
            initializer = self.converter.to_initializer(x)
            params = self.converter.to_params(x)
            self.initializer = initializer

            try:
                self.model.solve(initializer=initializer, params=params)
            except (ValueError, FloatingPointError) as err:
                print("[ERROR IN FITNESS EVALUATION]", err)
                return [np.inf]

            # idx = self.model.u > self.model.thr
            #
            # if not idx.any():
            #     return [np.inf]
            # elif self.model.u.size == idx.sum():
            #     return [np.inf]
            # elif np.allclose(self.model.u[idx], self.model.u[idx].mean()):
            #     return [np.inf]

            # Colorize the ladybird model.
            arr_color = self.model.colorize()

            # Store the colored object in the cache.
            self.cache[digest] = arr_color
        # end of if-else

        # Evaluate objectives.
        ladybird = self.model.create_image(0, arr_color)
        sum_obj = 0
        for obj in self.objectives:
            val = obj.compute(ladybird.convert("RGB"), self.targets)
            sum_obj += val

        return [sum_obj]

    def get_bounds(self):
        return (self.bounds_min, self.bounds_max)

    def save(self, 
             mode,
             dv,             
             generation=None,
             fitness=None,
             arr_color=None):

        dv = dv[None, :]
        params = self.converter.to_params(dv)
        init_states = self.converter.to_init_states(dv)
        init_pts = self.converter.to_init_pts(dv)        
        
        initializer = self.converter.to_initializer(dv)            
        self.model._initializer = initializer
        
        str_now = datetime.now().strftime('%Y%m%d-%H%M%S')
        if mode == "pop":
            fpath_model = pjoin(self.dpath_population,
                                "model_%s.json"%(str_now))            
            fpath_image = pjoin(self.dpath_population,
                                "image_%s.png"%(str_now))        
            
        elif mode == "best":            
            fpath_model = pjoin(self.dpath_best,
                                "model_%s.json"%(str_now))            
            fpath_image = pjoin(self.dpath_best,
                                "image_%s.png"%(str_now))        
        else:
            raise ValueError("mode should be 'pop' or 'best'")

        if arr_color is None:            
            digest = get_hash_digest(dv)            
            if digest not in self.cache:                
                try:
                    self.model.solve(init_states=init_states,
                                     params=params,
                                     initializer=initializer)
                    
                except (ValueError, FloatingPointError) as err:
                    return False
                
                arr_color = self.model.colorize() 
            else: 
                # Fetch the stored array from the cache.
                arr_color = self.cache[digest]
        # end of if

        self.model.save_model(fpath_model,
                              i=0,
                              init_states=init_states,
                              init_pts=init_pts,
                              params=params,
                              generation=generation,
                              fitness=fitness)
        
        self.model.save_image(fpath_image, i=0, arr_color=arr_color)
            
        return True
