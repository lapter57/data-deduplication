import glob
import os
import os.path as path
import shutil


def cleanup():
    os.system("docker-compose exec mongodb mongo data_deduplication --quiet --eval \"db.dropDatabase()\"")
    os.system("docker-compose stop")
    files = glob.glob('metrics/blocks/*')
    for file in files:
        if path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
    downloaded_files = glob.glob('metrics/downloaded_data/*')
    for file in downloaded_files:
        os.remove(file)


def start_dockers():
    os.system('docker-compose up --build -d mongodb')
    os.system('docker-compose up -d app')


def setup_context():
    if not path.exists('metrics/test_data'):
        os.makedirs('metrics/test_data')
    if not path.exists('metrics/blocks'):
        os.makedirs('metrics/blocks')
    if not path.exists('metrics/downloaded_data'):
        os.makedirs('metrics/downloaded_data')
    if not path.exists('metrics/graphs'):
        os.makedirs('metrics/graphs')
