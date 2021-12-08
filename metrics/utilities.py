import os
import os.path as path
import uuid
import random
import glob
import shutil
import string


def cleanup():
    os.system('docker stop $(docker ps -a -q)')
    os.system('docker rm -v mongo')
    files = glob.glob('metrics/blocks/*')
    for file in files:
        if path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
    downloaded_files = glob.glob('metrics/downloaded_data/*')
    for file in downloaded_files:
        os.remove(file)


def setup_context():
    if not path.exists('metrics/test_data'):
        os.makedirs('metrics/test_data')
    if not path.exists('metrics/blocks'):
        os.makedirs('metrics/blocks')
    if not path.exists('metrics/downloaded_data'):
        os.makedirs('metrics/downloaded_data')
    if not path.exists('metrics/graphs'):
        os.makedirs('metrics/graphs')
