import json
import os

import numpy as np

from utils import tools
import scipy.stats as stats


def gauss(mu, sigma, number):
    '''
    Return `number`-length truncated Gaussian sequence.

    Range: [mu - 3 sigma, mu + 3 sigma]

    Args:
        mu (int/float): mean
        sigma (int/float): variance       
        number (int): the length of truncated Gaussian sequence

    Returns:
        np.ndarray: a number-length truncated Gaussian sequence
    '''
    lower, upper = -3, 3
    X = stats.truncnorm(lower, upper, loc=mu, scale=sigma)
    return X.rvs(size=number)


def generate_mmlink_multibw(configs_list):
    ''' 
    Generate traces for mmlink to use.

    Args:
        configs_list (list): each element is a list containing a bunch of lists. Every sub list has four elements: mean, var, length, interval
            mean: mean of bandwidth
            var: variance of bandwidth
            length: how much points generated
            interval: how much points in one milleseconds

    Returns:
        dict, dict: traces, information of traces
    '''
    trace_dict = {}
    trace_info = {}
    seq = 0
    for configs in configs_list:
        seq = seq + 1
        last_time = 0
        timestamp = 0
        transfer = 0
        trace = ''
        trace_name = ''
        trace_desc = ''
        raw_trace_data = np.array([])
        for mean, var, length, interval in configs:
            if trace_name == '':
                trace_name = f'{mean}-{seq}'
            trace_desc = trace_desc + f'<{mean}-{var}-{length}-{interval}>'
            bw = gauss(mean, var, length)
            raw_trace_data = np.append(raw_trace_data, bw)
            for b in bw:
                transfer = transfer + b * 125 / interval
                last_time = last_time + 1
                if last_time >= interval:
                    last_time = 0
                    timestamp = timestamp + 1
                    while transfer >= 1500:
                        transfer = max(0, transfer - 1500)
                        trace = trace + str(timestamp) + '\n'
        trace_dict[trace_name] = trace
        trace_info[trace_name] = {
            'desc': trace_desc,
            'length': timestamp,
            'raw_data': raw_trace_data
        }
    return trace_dict, trace_info


class TraceLoader:
    'load the information of traces'

    def __init__(self,
                 trace_list: list,
                 trace_folder: str,
                 link_trace_save=1,
                 raw_save=1,
                 trace_info_save=1):
        '''
        initialize the traceloader

        Args:
        trace_list: information of traces to load
        trace_folder: path to save the traces
        link_trace_save:whether save the link_trace in trace_folder or not
        raw_save: whether save the raw_data in .npy or not
        trace_info_save: whether save the trace_info in .json or not

        '''
        self._trace_list = trace_list
        self._trace_folder = trace_folder
        self._link_trace_save = link_trace_save
        self._raw_save = raw_save
        self._trace_info_save = trace_info_save

    def load(self):
        self._link_trace_multibw_generator()

    def read_trace_info(self):
        return self.trace_info

    def read_link_trace(self):
        return self.link_trace

    def _link_trace_multibw_generator(self):
        '''
        Generate mahimahi traces that can have different bandwidth in different sections.

        Args:
            configs_list (list): each element is a list containing a bunch of lists. Every sub list has four elements: mean, var, length, interval
                mean: mean of bandwidth
                var: variance of bandwidth
                length: how much points generated
                interval: how much points in one milleseconds
                e.g. [ [ [ 12, 2, 130000, 1], ], [ [ 48, 8, 130000, 1], [ 24, 6, 130000, 1], ],]
            trace_path (str): folder to save traces

        Returns:
            dict: information of traces
        '''
        tools.clear_folder(self._trace_folder)
        link_trace, trace_info = generate_mmlink_multibw(self._trace_list)
        if self._link_trace_save:
            for trace in link_trace:
                with open(os.path.join(self._trace_folder, trace),
                          'w',
                          encoding='utf-8') as f:
                    f.write(link_trace[trace])

        
        for info in trace_info:
            raw_data = trace_info[info].pop('raw_data')
            raw_path = os.path.join(self._trace_folder, info + '.npy')
            trace_info[info]['raw_data'] = raw_path
            if self._raw_save:
                np.save(raw_path, raw_data)
        if self._trace_info_save:
            json.dump(
                trace_info,
                open(os.path.join(self._trace_folder, 'trace_info.json'),
                     'w',
                     encoding='utf-8'))
        self.link_trace = link_trace
        self.trace_info = trace_info
