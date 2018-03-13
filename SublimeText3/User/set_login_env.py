#!/usr/bin/env python

import subprocess
import os
import sys

def plugin_loaded():
    if sys.platform == 'linux':
        env_output = subprocess.check_output(["bash", '-l', '-c', '"env"'])

        for line in env_output.splitlines():
            line = line.decode().strip()
            if line:
                key, val = line.split('=')[0], '='.join(line.split('=')[1:])
                os.environ[key] = val
