import json
import os

import numpy as np

from utils import mmlink_trace, tools


def link_trace_generator(bw_list, length, interval, trace_path):
    mmlink_configs = []
    for bw, var in bw_list:
        mmlink_configs.append((bw, var, length, interval))
    link_trace = mmlink_trace.generate_mmlink(mmlink_configs)
    for trace in link_trace:
        with open(os.path.join(trace_path, trace), 'w', encoding='utf-8') as f:
            f.write(link_trace[trace])


def link_trace_multibw_generator(configs_list, trace_path):
    tools.clear_folder(trace_path)
    link_trace, trace_info = mmlink_trace.generate_mmlink_multibw(configs_list)
    for trace in link_trace:
        with open(os.path.join(trace_path, trace), 'w', encoding='utf-8') as f:
            f.write(link_trace[trace])
    for info in trace_info:
        raw_data = trace_info[info].pop('raw_data')
        raw_path = os.path.join(trace_path, info + '.npy')
        trace_info[info]['raw_data'] = raw_path
        np.save(raw_path, raw_data)
    json.dump(
        trace_info,
        open(os.path.join(trace_path, 'trace_info.json'),
             'w',
             encoding='utf-8'))
    return trace_info


if __name__ == '__main__':
    # bw_list = [(12, 0), (12, 1), (12, 2), (24, 0), (24, 1), (24, 2), (24, 4),(48, 0), (48, 1), (48, 2), (48, 4), (48, 8)]
    # length = 500
    # interval = 5
    # link_trace_generator(bw_list, length, interval, TRACE_PATH)
    TRACE_PATH = './traces'
    configs_list = [ [ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],]
    link_trace_multibw_generator(configs_list, TRACE_PATH)
