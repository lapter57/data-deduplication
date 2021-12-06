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
        if path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
    downloaded_files = glob.glob('metrics/downloaded_data/*')
    for file in downloaded_files:
        os.remove(file)


if __name__ == '__main__':
    work_dir = path.abspath(path.join(__file__, '../../'))
    os.chdir(work_dir)
    cleanup()
