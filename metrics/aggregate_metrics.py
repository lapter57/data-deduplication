import os
import os.path as path
import json
from decimal import *

import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd


def get_dir_size(dir_path: str) -> int:
    size = 0
    for dir_obj in os.scandir(dir_path):
        size += os.path.getsize(dir_obj)
    return size


def compute_deduplication(db_info: int, block_size: int, hash_function: str) -> float:
    src_data_dir = path.join('metrics/test_data')
    src_data_size = get_dir_size(src_data_dir)
    blocks_size = get_dir_size('metrics/blocks')
    deduplication_metric = src_data_size / (blocks_size + db_info)
    with open(f'metrics/deduplication_info_{block_size}_{hash_function}.json', 'w') as deduplication_outp:
        json.dump({'block_size': block_size,
                   'test_data_size': src_data_size,
                   'hash_function': hash_function,
                   'blocks_size': blocks_size}, deduplication_outp)
    if not path.exists('metrics/deduplication_general.json'):
        with open('metrics/deduplication_general.json', 'w') as metric_general:
            json.dump([{'block_size': block_size,
                       'hash_function': hash_function,
                       'deduplication_metric': deduplication_metric}], metric_general)
    else:
        with open('metrics/deduplication_general.json', 'r') as metric_general:
            general_deduplication = json.load(metric_general)
        general_deduplication.append({'block_size': block_size,
                                      'hash_function': hash_function,
                                      'deduplication_metric': deduplication_metric})
        with open('metrics/deduplication_general.json', 'w') as metric_general:
            json.dump(general_deduplication, metric_general)
    return deduplication_metric


def compute_time(metric: list, block_size: int, operation: str, hash_function: str) -> float:
    speeds = [item['file_size'] / item['time'] for item in metric]
    median_speed = sorted(speeds)[len(speeds)//2]
    if not path.exists(f'metrics/{operation}.json'):
        with open(f'metrics/{operation}.json', 'w') as first_metric:
            json.dump({hash_function: [{'block_size': block_size, 'speed': median_speed}]}, first_metric)
    else:
        with open(f'metrics/{operation}.json', 'r') as metric_src:
            metric_data = json.load(metric_src)
        metric_data.setdefault(hash_function, []).append({'block_size': block_size, 'speed': median_speed})
        with open(f'metrics/{operation}.json', 'w') as metric_src:
            json.dump(metric_data, metric_src)

def draw_graph(metric: str, hash_function: str = ''):
    if metric == 'deduplication':
        with open('metrics/deduplication_general.json') as metric_src:
            metric_data = json.load(metric_src)
        metric_values = [val['deduplication_metric'] for val in metric_data]
        block_sizes = [val['block_size'] for val in metric_data]
        ax = sns.barplot(x=block_sizes, y=metric_values)
        ax.set(xlabel='block size', ylabel='deduplication')
        ax.figure.savefig(f'metrics/graphs/barplot_{metric}_{hash_function}.png')
        plt.close()
        ax = sns.lineplot(x=block_sizes, y=metric_values)
        ax.set(xlabel='block size', ylabel='deduplication')
        ax.figure.savefig(f'metrics/graphs/lineplot_{metric}_{hash_function}.png')
        plt.close()
    elif metric in ['upload', 'download']:
        with open(f'metrics/{metric}.json', 'r') as metric_data:
            time_metric = json.load(metric_data)
        hash_functions = list(time_metric.keys())
        t = []
        for i in hash_functions:
            for j in time_metric[i]:
                t.append((i, j['speed'], j['block_size']))
        fig_data = pd.DataFrame(t, columns=['hash function', 'speed', 'block size'])
        fig = sns.lineplot(data=fig_data, x='block size', y='speed', hue='hash function')
        fig.set(xlabel='block size', ylabel=f'{metric} speed')
        fig.figure.suptitle(f'Median time of {metric}')
        fig.figure.savefig(f'metrics/graphs/{metric}.png')
        plt.close()


if __name__ == '__main__':
    work_dir = path.abspath(path.join(__file__, '../../'))
    os.chdir(work_dir)
    draw_graph('upload')
    draw_graph('download')
