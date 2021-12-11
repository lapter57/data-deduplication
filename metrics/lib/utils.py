import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

GET_TOTAL_SIZE_DIR_CMD = "du -ab {} | head -n -1 | awk '{{s+=$1}} END {{s+=0 ; print s}}'"
SIZE_NAME = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def create_path(path, is_recreate=True):
    recreated_path = Path(path)
    if is_recreate:
        shutil.rmtree(recreated_path, ignore_errors=True)
    recreated_path.mkdir(parents=True, exist_ok=True)
    return recreated_path


def human_read_to_bytes(size):
    num_unit = size.split()
    num, unit = int(num_unit[0]), num_unit[1]
    factor = 1024 ** SIZE_NAME.index(unit)
    return num * factor


def get_dir_size_bytes(dir_path):
    return int(subprocess.check_output(GET_TOTAL_SIZE_DIR_CMD.format(dir_path), shell=True))


def block_sizes_generator(max_size, min_size, denominator):
    size = max_size
    while size >= min_size:
        yield int(size)
        size /= denominator


def start_dockers(project_path):
    cwd = os.getcwd()
    os.chdir(project_path)
    os.system("docker-compose up --build -d mongodb")
    os.system("docker-compose up -d app")
    time.sleep(60)
    os.chdir(cwd)


def stop_dockers(project_path, storage_path):
    cwd = os.getcwd()
    os.chdir(project_path)
    os.system("docker-compose exec mongodb mongo data_deduplication --quiet --eval 'db.dropDatabase()'")
    os.system(f"docker-compose exec app rm -rf {storage_path}")
    os.system("docker-compose stop")
    os.chdir(cwd)


def get_storage_size(project_path, storage_path):
    cwd = os.getcwd()
    os.chdir(project_path)
    blocks_size = int(subprocess.check_output(f"docker-compose exec app {GET_TOTAL_SIZE_DIR_CMD.format(storage_path)}",
                                              shell=True))
    os.chdir(cwd)
    return blocks_size


def get_mongo_data_size(project_path):
    cwd = os.getcwd()
    os.chdir(project_path)
    get_mongo_data = subprocess.run(
        ["docker-compose exec mongodb mongo data_deduplication --quiet --eval 'db.stats()'"],
        capture_output=True, text=True, shell=True)
    db_size = json.loads(get_mongo_data.stdout)["dataSize"]
    os.chdir(cwd)
    return db_size


def plot_deduplication(hash_function, hash_function_info_path, plots_path):
    with open(os.path.join(hash_function_info_path, "deduplication.json"), "r") as deduplication_info_file:
        deduplication_info = json.load(deduplication_info_file)
    deduplications = [val["deduplication"] for val in deduplication_info]
    deduplications_with_db = [val["deduplication_with_db"] for val in deduplication_info]
    block_sizes = [val["block_size"] for val in deduplication_info]

    ax = sns.barplot(x=block_sizes, y=deduplications)
    ax.set(xlabel="block size (B)", ylabel="deduplication")
    ax.figure.savefig(os.path.join(plots_path, f"barplot_deduplication_{hash_function}.png"))
    plt.close()

    ax = sns.barplot(x=block_sizes, y=deduplications_with_db)
    ax.set(xlabel="block size (B)", ylabel="deduplication_with_db")
    ax.figure.savefig(os.path.join(plots_path, f"barplot_deduplication_with_db_{hash_function}.png"))
    plt.close()

    ax = sns.lineplot(x=block_sizes, y=deduplications)
    ax.set(xlabel="block size (B)", ylabel="deduplication")
    ax.figure.savefig(os.path.join(plots_path, f"lineplot_deduplication_{hash_function}.png"))
    plt.close()

    ax = sns.lineplot(x=block_sizes, y=deduplications_with_db)
    ax.set(xlabel="block size (B)", ylabel="deduplication_with_db")
    ax.figure.savefig(os.path.join(plots_path, f"lineplot_deduplication_with_db_{hash_function}.png"))
    plt.close()


def plot_time(hash_function, hash_function_info_path, plots_path):
    for metric in ["upload", "download"]:
        with open(os.path.join(hash_function_info_path, f"{metric}_{hash_function}.json"), "r") as time_info_file:
            time_info = json.load(time_info_file)
        hash_functions = list(time_info.keys())
        t = [(i, j["median_speed"], j["block_size"]) for i in hash_functions for j in time_info[i]]
        fig_data = pd.DataFrame(t, columns=["hash function", "median speed", "block size"])
        fig = sns.lineplot(data=fig_data, x="block size", y="median speed", hue="hash function")
        fig.set(xlabel="block size (B)", ylabel=f"{metric} median speed (B/s)")
        fig.figure.suptitle(f"Median time of {metric}")
        fig.figure.savefig(os.path.join(plots_path, f"{metric}_{hash_function}.png"))
        plt.close()
