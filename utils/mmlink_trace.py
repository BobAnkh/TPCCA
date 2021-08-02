import numpy as np
import scipy.stats as stats


def gauss(mu, sigma, number):
    '''
    Return `number`-length truncated Gaussian sequence.

    Range: [mu - 3 sigma, mu + 3 sigma]

    Args:
        mu (int/float): mean
        sigma (int/float): variance       #???
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
            for b in bw: #???
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


if __name__ == '__main__': #???
    generate_mmlink_multibw([[(12, 0, 10, 1)], [(24, 0, 10, 1),
                                                (48, 0, 10, 1)]])
