import json
import os
import random
import shutil
import tempfile
import uuid
from datetime import datetime

import magic
import numpy as np
import requests
from loguru import logger
from ruamel.yaml import YAML
from tqdm import tqdm

from lib.utils import get_dir_size_bytes, block_sizes_generator, stop_dockers, plot_deduplication, plot_time, \
    human_read_to_bytes, start_dockers, get_storage_size, \
    get_mongo_data_size, create_path, write_file, insert_into_array


class Tester:
    def __init__(self, config):
        self.config = config
        self.yaml = YAML(typ="safe")
        self.mime = magic.Magic(mime=True)
        self.test_data_size = self.__create_test_data()

    def __create_test_data(self):
        def modify_file(base, min_change_size, max_change_size, min_change_blocks, max_change_blocks, remove_percentage):
            def get_add_status():
                return random.randint(1, 1000) >= (remove_percentage * 10)

            current_len = len(base)
            modify_size = random.randint(min_change_size, max_change_size)
            modify_blocks = random.randint(min_change_blocks, max_change_blocks)
            blocks = [(get_add_status(), random.randint(0, current_len), size) for size in
                      np.random.multinomial(modify_size, np.ones(modify_blocks) / modify_blocks, size=1)[0]]
            blocks = sorted(blocks, reverse=True)
            for status, pos, size in blocks:
                if not status:
                    if pos + size <= current_len:
                        base = base[:pos] + base[pos + size:]
                    else:
                        base = base[:pos]
                else:
                    add_data = os.urandom(size)
                    end_pos = size + pos
                    if end_pos > current_len:
                        end_pos = current_len
                    base = base_file[:pos] + add_data + base_file[end_pos:]
            return base

        def fit_size_requirements(file, min_size, max_size):
            current_size = len(file)
            if min_size <= current_size <= max_size:
                return file
            elif current_size > max_size:
                return file[:max_size]
            elif current_size < min_size:
                add_size = min_size - current_size
                add_data = os.urandom(add_size)
                insert_pos = random.randint(0, min_size - add_size)
                return insert_into_array(file, add_data, insert_pos)

        data_path = self.config.data.path
        if self.config.data.need_create:
            create_path(data_path)
            logger.info("Generating data...")
            data_size = human_read_to_bytes(self.config.data.size)
            min_file_size = human_read_to_bytes(self.config.data.min_file_size)
            max_file_size = human_read_to_bytes(self.config.data.max_file_size)
            min_change_size = human_read_to_bytes(self.config.data.min_change_size)
            max_change_size = human_read_to_bytes(self.config.data.max_change_size)

            max_change_blocks = int(self.config.data.max_change_blocks)
            min_change_blocks = int(self.config.data.min_change_blocks)
            remove_percentage = int(self.config.data.remove_shance_percentage)
            base_file = os.urandom(min_file_size)
            while get_dir_size_bytes(data_path) < data_size:
                file_path = os.path.join(data_path, f"{uuid.uuid4()}.txt")
                base_file = modify_file(base_file, min_change_size, max_change_size, min_change_blocks,
                                        max_change_blocks, remove_percentage)
                base_file = fit_size_requirements(base_file, min_file_size, max_file_size)
                write_file(file_path, base_file)
        total_size = get_dir_size_bytes(data_path)
        logger.info(f"Test dir {data_path} with size {total_size / 1024 / 1024:.2f} MB")
        return total_size

    def test(self):
        storage_path = self.config.project.storage_path
        project_path = self.config.project.path
        plots_path = create_path(self.config.result.plots_path)
        data_path = create_path(self.config.result.data_path)

        max_block_size = human_read_to_bytes(self.config.block.max_size)
        min_block_size = human_read_to_bytes(self.config.block.min_size)
        block_size_denominator = self.config.block.denominator
        test_files = os.listdir(os.path.join(self.config.data.path))

        stop_dockers(project_path, storage_path)
        try:
            for hash_function in self.config.block.hash_functions:
                logger.info(f"Processing {hash_function}")
                hash_function_info_path = create_path(os.path.join(data_path, hash_function.lower()), False)
                for block_size in block_sizes_generator(max_block_size, min_block_size, block_size_denominator):
                    logger.info(f"Processing block {block_size} bytes")
                    self.__setup_docker_compose_config(hash_function, block_size)
                    start_dockers(project_path)
                    file_ids, total_upload_time = self.__test_upload_data(test_files)
                    total_download_time = self.__test_download_file(file_ids)
                    self.__compute_deduplication(hash_function, block_size, hash_function_info_path)
                    self.__compute_time(total_upload_time, hash_function, block_size, f"upload_{hash_function}",
                                        hash_function_info_path)
                    self.__compute_time(total_download_time, hash_function, block_size, f"download_{hash_function}",
                                        hash_function_info_path)
                    stop_dockers(project_path, storage_path)
                plot_deduplication(hash_function, hash_function_info_path, plots_path)
                plot_time(hash_function, hash_function_info_path, plots_path)
        except Exception as e:
            stop_dockers(project_path, storage_path)
            raise e

    def __setup_docker_compose_config(self, hash_function, block_size):
        with open(os.path.join(self.config.project.path, "docker-compose.yml"), "r") as docker_compose_file:
            docker_compose_dict = self.yaml.load(docker_compose_file)

        for index, env_var in enumerate(docker_compose_dict["services"]["app"]["environment"]):
            if "HASH_TYPE" in env_var.split("="):
                docker_compose_dict["services"]["app"]["environment"][index] = f"HASH_TYPE={hash_function}"
            if "BLOCK_SIZE" in env_var.split("="):
                docker_compose_dict["services"]["app"]["environment"][index] = f"BLOCK_SIZE={block_size}"
            if "BASE_PATH" in env_var.split("="):
                docker_compose_dict["services"]["app"]["environment"][
                    index] = f"BASE_PATH={self.config.project.storage_path}"

        with open(os.path.join(self.config.project.path, "docker-compose.yml"), "w") as docker_compose_file:
            self.yaml.dump(docker_compose_dict, docker_compose_file)

    def __test_upload_data(self, test_files):
        total_upload_time = []
        files_ids = []
        for upload_file_name in tqdm(test_files, desc="Uploading files"):
            upload_file_path = os.path.join(self.config.data.path, upload_file_name)
            with open(upload_file_path, "rb") as upload_file:
                upload_start_time = datetime.now()
                upload_data = requests.post(f"{self.config.project.api_url}/file",
                                            files={"file": (upload_file_path,
                                                            upload_file,
                                                            self.mime.from_file(upload_file_path))})
                upload_time = (datetime.now() - upload_start_time).total_seconds()
                if upload_data.status_code // 100 == 2:
                    total_upload_time.append({"time": upload_time,
                                              "file_size": os.stat(upload_file_path).st_size})
                    files_ids.append(
                        {"file_id": upload_data.text, "file_ext": os.path.splitext(upload_file_name)[1][1:]})
        return files_ids, total_upload_time

    def __test_download_file(self, file_ids):
        total_download_time = []
        download_dir_path = create_path(os.path.join(tempfile.gettempdir(), "data_dedup_downloaded_test_data"))
        for file_info in tqdm(file_ids, desc="Downloading files"):
            download_file_path = os.path.join(download_dir_path, f"{file_info['file_id']}.{file_info['file_ext']}") \
                if file_info["file_ext"] else os.path.join(download_dir_path, file_info["file_id"])
            with open(download_file_path, "wb") as download_file:
                download_start_time = datetime.now()
                download_data = requests.get(f"{self.config.project.api_url}/file/{file_info['file_id']}",
                                             allow_redirects=True)
                download_file.write(download_data.content)
                download_time = (datetime.now() - download_start_time).total_seconds()
                if download_data.status_code // 100 == 2:
                    if file_info["file_ext"]:
                        total_download_time.append({"time": download_time,
                                                    "file_size": os.stat(download_file_path).st_size})
                    else:
                        total_download_time.append({"time": download_time,
                                                    "file_size": os.stat(download_file_path).st_size})
        shutil.rmtree(download_dir_path)
        return total_download_time

    def __compute_deduplication(self, hash_function, block_size, info_dir_path):
        blocks_size = get_storage_size(self.config.project.path, self.config.project.storage_path)
        db_size = get_mongo_data_size(self.config.project.path)

        deduplication = self.test_data_size / blocks_size
        deduplication_with_db = self.test_data_size / (blocks_size + db_size)

        saved_info = dict(block_size=block_size,
                          test_data_size=self.test_data_size,
                          hash_function=hash_function,
                          blocks_size=blocks_size,
                          deduplication=deduplication,
                          deduplication_with_db=deduplication_with_db)
        deduplication_info_path = os.path.join(info_dir_path, "deduplication.json")
        if not os.path.exists(deduplication_info_path):
            with open(deduplication_info_path, "w") as deduplication_info_file:
                json.dump([saved_info], deduplication_info_file)
        else:
            with open(deduplication_info_path, "r") as deduplication_info_file:
                deduplication_info = json.load(deduplication_info_file)
            deduplication_info.append(saved_info)
            with open(deduplication_info_path, "w") as deduplication_info_file:
                json.dump(deduplication_info, deduplication_info_file)

    @staticmethod
    def __compute_time(metric, hash_function, block_size, operation_name, info_dir_path):
        speeds = [item["file_size"] / item["time"] for item in metric]
        median_speed = np.median(speeds)

        time_info_path = os.path.join(info_dir_path, f"{operation_name}.json")
        if not os.path.exists(time_info_path):
            with open(time_info_path, "w") as time_info_file:
                json.dump({hash_function: [{"block_size": block_size, "median_speed": median_speed}]}, time_info_file)
        else:
            with open(time_info_path, "r") as time_info_file:
                metric_data = json.load(time_info_file)
            metric_data.setdefault(hash_function, []).append({"block_size": block_size, "median_speed": median_speed})
            with open(time_info_path, "w") as time_info_file:
                json.dump(metric_data, time_info_file)
