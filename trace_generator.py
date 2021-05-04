from utils import mmlink_trace
import os

TRACE_PATH = './traces'


def link_trace_generator(bw_list, length, interval):
    mmlink_configs = []
    for bw, var in bw_list:
        mmlink_configs.append((bw, var, length, interval))
    link_trace = mmlink_trace.generate_mmlink(mmlink_configs)
    for trace in link_trace:
        with open(os.path.join(TRACE_PATH, trace), 'w', encoding='utf-8') as f:
            f.write(link_trace[trace])


if __name__ == '__main__':
    bw_list = [(12, 0), (12, 1), (12, 2), (24, 0), (24, 1), (24, 2), (24, 4),(48, 0), (48, 1), (48, 2), (48, 4), (48, 8)]
    length = 500
    interval = 5
    link_trace_generator(bw_list, length, interval)