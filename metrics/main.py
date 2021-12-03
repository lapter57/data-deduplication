import os
import os.path as path
import subprocess

import ruamel.yaml


GET_MONGO_SIZE_COMMAND = 'docker-compose exec mongodb mongo data_deduplication --quiet --eval "db.stats()"'

work_dir = path.abspath(path.join(__file__, '../../'))
os.chdir(work_dir)


app_ports = ruamel.yaml.scalarstring.DoubleQuotedScalarString('8080:8080')
mongo_ports = ruamel.yaml.scalarstring.DoubleQuotedScalarString('27017:27017')
block_size = 256
while block_size <= 131072:
    docker_compose = {'version': '3'}
    services = {
        'mongodb': {
            'image': 'mongo:bionic',
            'environment': {
                'MONGO_INIT_DATABASE': 'data_deduplication',
                'BLOCK_SIZE': block_size
            },
            'ports': [mongo_ports]
        },
        'app': {
            'build': '.',
            'expose': [8080],
            'ports': [app_ports],
            'depends_on': ['mongodb'],
            'environment': ['PORT=8080','DB_URI=mongodb://mongodb:27017/data_deduplication']
        }
    }
    docker_compose['services'] = services
    with open(f'docker-compose-tmp.yml', 'w') as docker_compose_obj:
        yaml = ruamel.yaml.YAML()
        yaml.dump(docker_compose, docker_compose_obj)
    get_mongo_data_command = GET_MONGO_SIZE_COMMAND.split()[0]
    get_mongo_data_args = ' '.join(GET_MONGO_SIZE_COMMAND.split()[1::])
    get_mongo_data = subprocess.Popen([get_mongo_data, get_mongo_data_args], stdout=subprocess.PIPE, srderr=subprocess.PIPE)
    mongo_data, mongo_err = get_mongo_data.communicate()
    block_size *= 2
