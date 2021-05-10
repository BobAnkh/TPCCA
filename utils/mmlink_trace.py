import scipy.stats as stats
import numpy as np


def gauss(mu, sigma, number):
    '''
    Return `number`-length truncated Gaussian sequence

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


def generate_mmlink(configs):
    trace_dict = {}
    for mean, var, length, interval in configs:
        bw = gauss(mean, var, length)
        last_time = 0
        timestamp = 0
        transfer = 0
        trace = ''
        for b in bw:
            b = max(0, b)
            transfer = transfer + b * 125 / interval
            last_time = last_time + 1
            if last_time >= interval:
                last_time = 0
                timestamp = timestamp + 1
                while transfer >= 1500:
                    transfer = max(0, transfer - 1500)
                    trace = trace + str(timestamp) + '\n'
        trace_dict[f'{mean}-{var}'] = trace
    return trace_dict


def generate_mmlink_multibw(configs_list):
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
        for mean, var, length, interval in configs:
            if trace_name == '':
                trace_name = f'{mean}-{seq}'
            trace_desc = trace_desc + f'<{mean}-{var}-{length}-{interval}>'
            bw = gauss(mean, var, length)
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
        trace_info[trace_name] = {'desc': trace_desc, 'length': timestamp}
    return trace_dict, trace_info


if __name__ == '__main__':
    # generate_mmlink([(12, 2, 10, 1), (48, 2, 10, 1)])
    generate_mmlink_multibw([[(12, 0, 10, 1)],[(24, 0, 10, 1), (48, 0, 10, 1)]])
