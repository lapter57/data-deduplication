import os
import os.path as path
import datetime
import time
import subprocess
import json

import magic
import requests
import ruamel.yaml

from aggregate_metrics import compute_deduplication


APP_URL = 'http://localhost:8080'

work_dir = path.abspath(path.join(__file__, '../../'))
os.chdir(work_dir)

source_compose = ruamel.yaml.YAML(typ='safe')
with open('docker-compose.yml', 'r') as src_f:
    source_compose = ruamel.yaml.load(src_f)
block_size = 256
upload_metrics = {}
download_metrics = {}
while block_size <= 256:
    if len(source_compose['services']['app']['environment']) == 1:
        source_compose['services']['app']['environment'].append(f'BLOCK_SIZE={block_size}')
    else:
        source_compose['services']['app']['environment'][1] = f'BLOCK_SIZE={block_size}'
    with open('docker-compose.yml', 'w') as src_f:
        target_compose = ruamel.yaml.YAML()
        target_compose.dump(source_compose, src_f)
    os.system('docker-compose up --build -d')
    time.sleep(120)
    for file_to_upload in os.listdir(path.join('metrics/test_data')):
        # upload data
        file_format = file_to_upload.split('.')[-1]
        upload_metrics[block_size] = {file_format: []}
        download_metrics[block_size] = {file_format: []}
        with open(path.join(f'metrics/test_data/{file_to_upload}'), 'rb') as upload_file:
            mime = magic.Magic(mime=True)
            upload_start_time = datetime.datetime.now()
            upload_data = requests.post(f'{APP_URL}/api/file', files={'file': (f'metrics/test_data/{file_to_upload}',
                                                                                upload_file,
                                                                                mime.from_file(f'metrics/test_data/{file_to_upload}'))})
            upload_time = (datetime.datetime.now() - upload_start_time).total_seconds()
            file_id = upload_data.text
            upload_metrics[block_size][file_format].append({'time': upload_time,
                                                            'file_size': os.stat(f'metrics/test_data/{file_to_upload}').st_size})
        # download data
        with open(path.join(f'metrics/downloaded_data/{file_id}.{file_format}'), 'wb') as download_file:
            download_start_time = datetime.datetime.now()
            download_data = requests.get(f'{APP_URL}/api/file/{file_id}', allow_redirects=True)
            download_file.write(download_data.content)
            download_time = (datetime.datetime.now() - download_start_time).total_seconds()
        download_metrics[block_size][file_format].append({'time': download_time,
                                                          'file_size': os.stat(f'metrics/downloaded_data/{file_id}.{file_format}').st_size})
    get_mongo_data = subprocess.run(['docker-compose exec mongodb mongo data_deduplication --quiet --eval "db.stats()"'], capture_output=True, text=True, shell=True)
    mongo_info = json.loads(get_mongo_data.stdout)

    deduplication_metrics = compute_deduplication(mongo_info['dataSize'])
    block_size *= 2
