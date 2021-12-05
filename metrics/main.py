import os
import os.path as path
import subprocess

import requests
import ruamel.yaml
import pathlib


GET_MONGO_SIZE_COMMAND = 'docker-compose exec mongodb mongo data_deduplication --quiet --eval "db.stats()"'
APP_URL = 'http://localhost:8080'

work_dir = path.abspath(path.join(__file__, '../../'))
os.chdir(work_dir)

source_compose = ruamel.yaml.YAML(typ='safe')
with open('docker-compose.yml', 'r') as src_f:
    source_compose = ruamel.yaml.load(src_f)
block_size = 256

while block_size <= 256:
    if len(source_compose['services']['app']['environment']) == 1:
        source_compose['services']['app']['environment'].append(f'BLOCK_SIZE={block_size}')
    else:
        source_compose['services']['app']['environment'][1] = f'BLOCK_SIZE={block_size}'
    with open('docker-compose.yml', 'w') as src_f:
        target_compose = ruamel.yaml.YAML()
        target_compose.dump(source_compose, src_f)
    os.system('docker-compose up --build -d')
    with open(path.join('metrics/test_data/test_file.txt'), 'r') as upload_file:
        upload_data = requests.post(f'{APP_URL}/api/file', files={'test_file.txt': upload_file})
        print(upload_data)
    #download data
    
    get_mongo_data = os.system(GET_MONGO_SIZE_COMMAND)
    block_size *= 2
