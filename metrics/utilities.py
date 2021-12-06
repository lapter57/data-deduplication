import os
import os.path as path
import glob
import shutil


def cleanup():
    os.system('docker stop $(docker ps -a -q)')
    os.system('docker rm $(docker ps -a -q)')
    os.system('docker rmi $(docker images -a -q)')
    files = glob.glob('metrics/blocks/*')
    for file in files:
        os.remove(file)


if __name__ == '__main__':
    work_dir = path.abspath(path.join(__file__, '../../'))
    os.chdir(work_dir)
    cleanup()
