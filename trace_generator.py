import json
import os

import numpy as np

from utils import mmlink_trace, tools


def link_trace_multibw_generator(configs_list, trace_path):
    '''
    Generate mahimahi traces that can have different bandwidth in different sections.

    Args:
        configs_list (list): each element is a list containing a bunch of lists. Every sub list has four elements: mean, var, length, interval
            mean: mean of bandwidth
            var: variance of bandwidth
            length: how much points generated
            interval: how much points in one milleseconds
        trace_path (str): folder to save traces

    Returns:
        dict: information of traces
    '''
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
    TRACE_PATH = './traces'
    configs_list = [ [ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],[ [ 12, 2, 130000, 1,],],]
    link_trace_multibw_generator(configs_list, TRACE_PATH)
