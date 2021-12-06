import os
import os.path as path
import json

def get_dir_size(dir_path: str):
    size = 0
    for dir_obj in os.scandir(dir_path):
        size += os.path.getsize(dir_obj)
    return size


def compute_deduplication(db_info: int, block_size: int):
    src_data_dir = path.join('metrics/test_data')
    src_data_size = get_dir_size(src_data_dir)
    blocks_size = get_dir_size('metrics/blocks')
    deduplication_metric = src_data_size / (blocks_size + db_info)
    with open(f'deduplication_info_{block_size}.json', 'w') as deduplication_outp:
        json.dump({'block_size': block_size,
                   'test_data_size': src_data_size,
                   'blocks_size': blocks_size}, deduplication_outp)
    return compute_deduplication

def compute_time(metric: dict, **kwargs):
    time_metric = {}
    total_time = 0
    for block_size in metric:
        for file_type in metric[block_size]:
            for item in metric[block_size][file_type]:
                current_time = item['time']
                print(current_time)
                print(type(current_time))
                total_time += current_time
        time_metric[block_size] = {file_type: total_time/len(metric[block_size][file_type])}
        total_time = 0
    print(time_metric)
    return time_metric


if __name__ == '__main__':
    #compute_deduplication(1)
    compute_time({256: {'txt': [{'time': 0.037528, 'file_size': 6}]}})
