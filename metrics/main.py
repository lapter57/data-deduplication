import os
import os.path as path
import datetime
import time
import subprocess
import json
import random
import uuid

import magic
import requests
import ruamel.yaml

from aggregate_metrics import compute_deduplication, compute_time, draw_graph, get_dir_size
from utilities import cleanup, gen_test_data

# 'SHA-512'
# 32768


APP_URL = 'http://localhost:8080'

work_dir = path.abspath(path.join(__file__, '../../'))
os.chdir(work_dir)

while get_dir_size('metrics/test_data') < 5368709120:
    print('Generate new test file')
    gen_test_data()
    

source_compose = ruamel.yaml.YAML(typ='safe')
with open('docker-compose.yml', 'r') as src_f:
    source_compose = ruamel.yaml.load(src_f)
block_size = 4
for hash_function in ['SHA-256', 'MURMUR3_128']:
    while block_size <= 65536:
        total_upload_time = []
        total_download_time = []
        for index, env_var in enumerate(source_compose['services']['app']['environment']):
            if 'BLOCK_SIZE' in env_var.split('='):
                source_compose['services']['app']['environment'][index] = f'BLOCK_SIZE={block_size}'
            if 'HASH_TYPE' in env_var.split('='):
                source_compose['services']['app']['environment'][index] = f'HASH_TYPE={hash_function}'
        #print(source_compose)
        with open('docker-compose.yml', 'w') as src_f:
            target_compose = ruamel.yaml.YAML()
            target_compose.dump(source_compose, src_f)
        print(hash_function)
        os.system('docker-compose up --build -d')
        time.sleep(60)
        for file_to_upload in os.listdir(path.join('metrics/test_data')):
            # upload data
            file_format = file_to_upload.split('.')[-1]
            with open(path.join(f'metrics/test_data/{file_to_upload}'), 'rb') as upload_file:
                mime = magic.Magic(mime=True)
                upload_start_time = datetime.datetime.now()
                upload_data = requests.post(f'{APP_URL}/api/file', files={'file': (f'metrics/test_data/{file_to_upload}',
                                                                                    upload_file,
                                                                                    mime.from_file(f'metrics/test_data/{file_to_upload}'))})
                upload_time = (datetime.datetime.now() - upload_start_time).total_seconds()
                total_upload_time.append({'time': upload_time,
                                        'file_size': os.stat(f'metrics/test_data/{file_to_upload}').st_size})
                file_id = upload_data.text
                if file_id[0] == '{':
                    continue
            # download data
            with open(path.join(f'metrics/downloaded_data/{file_id}.{file_format}'), 'wb') as download_file:
                download_start_time = datetime.datetime.now()
                download_data = requests.get(f'{APP_URL}/api/file/{file_id}', allow_redirects=True)
                download_file.write(download_data.content)
                download_time = (datetime.datetime.now() - download_start_time).total_seconds()
                total_download_time.append({'time': download_time,
                                            'file_size': os.stat(f'metrics/downloaded_data/{file_id}.{file_format}').st_size})
        get_mongo_data = subprocess.run(['docker-compose exec mongodb mongo data_deduplication --quiet --eval "db.stats()"'], capture_output=True, text=True, shell=True)
        mongo_info = json.loads(get_mongo_data.stdout)
        deduplication_metric = compute_deduplication(mongo_info['dataSize'], block_size, hash_function)
        compute_time(total_upload_time, block_size, 'upload', hash_function)
        compute_time(total_download_time, block_size, 'download', hash_function)
        cleanup()
        block_size *= 2
    draw_graph('deduplication', hash_function)
    block_size = 4
draw_graph('upload')
draw_graph('download')
