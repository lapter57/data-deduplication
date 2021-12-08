import os
import os.path as path
import uuid
import random
import glob
import shutil
import string


def cleanup():
    os.system('docker stop $(docker ps -a -q)')
    os.system('docker rm $(docker ps -a -q)')
    os.system('docker rmi $(docker images -a -q)')
    files = glob.glob('metrics/blocks/*')
    for file in files:
        if path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
    downloaded_files = glob.glob('metrics/downloaded_data/*')
    for file in downloaded_files:
        os.remove(file)


def gen_test_data():
    mb_file_size = random.randint(1, 8)
    current_file_name = f'metrics/test_data/{uuid.uuid4()}.txt'
    with open(current_file_name, 'wb') as test_file:
        while os.fstat(test_file.fileno()).st_size < mb_file_size * 1024**2:
            test_file.write(str([random.choice(string.ascii_letters) for _ in range(10000)]).encode('utf-8'))
