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


if __name__ == '__main__':
    generate_mmlink([(12, 2, 100, 1)])
