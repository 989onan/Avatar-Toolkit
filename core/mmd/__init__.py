# -*- coding: utf-8 -*-
# Copyright 2014 MMD Tools authors
# This file was originally part of the MMD Tools add-on for Blender
# You can find MMD Tools here: https://github.com/MMD-Blender/blender_mmd_tools
# Neoneko has modified this file to work with Avatar Toolkit and may of made changes or improvements.
# MMD Tools is licensed under the terms of the GNU General Public License version 3 (GPLv3) same as Avatar Toolkit.

import os
import tomllib 

# This is a temporary workaround i be changing how MMD  Tools works later when it comes to getting version number.

try:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir)) 
    manifest_path = os.path.join(root_dir, 'blender_manifest.toml')
    
    if os.path.exists(manifest_path):
        with open(manifest_path, 'rb') as f:
            manifest = tomllib.load(f)
        AVATAR_TOOLKIT_VERSION = manifest.get('version', '0.2.1') 
    else:
        AVATAR_TOOLKIT_VERSION = '0.2.1' 
except Exception:
    AVATAR_TOOLKIT_VERSION = '0.2.1'  
