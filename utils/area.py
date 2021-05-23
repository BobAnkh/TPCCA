import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from utils import parseTputDelay, tools


def calculate_area(time_list, tput_list, start_time, end_time, standard_bw):
    area_sum = 0
    count = 0
    for i, t in enumerate(time_list):
        if t < start_time:
            continue
        if t >= end_time:
            break
        area_sum = area_sum + abs(standard_bw - tput_list[i])
        count = count + 1
    return area_sum / count * (end_time - start_time)


def calculate_area_detail(time_list, tput_list, start_time, end_time,
                          standard_bw):
    area_sum = 0
    for i, t in enumerate(time_list):
        if i < start_time:
            continue
        if i >= end_time:
            break
        area_sum = area_sum + abs(standard_bw -
                                  tput_list[i]) * (time_list[i + 1] - t)
    return area_sum / (time_list[end_time] - time_list[start_time])


def wnd_detect(time_list, start_time, start_seq, end_time, wnd_size):
    wnd_end = -1
    end_seq = -1
    error = -1
    if time_list[start_seq] != start_time:
        return wnd_end, end_seq, error
    for ii, tt in enumerate(time_list[start_seq:]):
        if tt >= end_time:
            return wnd_end, end_seq, error
        if tt >= start_time + wnd_size:
            wnd_end = tt
            end_seq = ii + start_seq
            error = 0
            return wnd_end, end_seq, error
    return wnd_end, end_seq, error


def stable_detect(time_list, tput_list, start_time, end_time, wnd_size,
                  move_size, wnd_num, mean_oscillation, var_oscillation):
    for i, t in enumerate(time_list):
        if t < start_time:
            continue
        if t >= end_time:
            return end_time
        wnd_list = []
        for num in range(wnd_num):
            wnd_start, start_seq, error = wnd_detect(time_list, t, i, end_time,
                                                     move_size * num)
            if error == -1:
                return end_time
            wnd_end, end_seq, error = wnd_detect(time_list, wnd_start,
                                                 start_seq, end_time, wnd_size)
            if error == -1:
                return end_time
            wnd_mean = np.mean(tput_list[start_seq:end_seq + 1])
            wnd_var = np.var(tput_list[start_seq:end_seq + 1])
            wnd_list.append(np.array([wnd_mean, wnd_var]))
            if num == int(wnd_num / 2):
                stable_mark = int((start_seq + end_seq) / 2)
        wnd_list = np.array(wnd_list)
        # print(np.var(wnd_list[:, 0]) , np.var(wnd_list[:, 1]))
        if np.var(wnd_list[:, 0]) <= mean_oscillation and np.var(
                wnd_list[:, 1]) <= var_oscillation:
            return stable_mark


def plot_area(ccp_algs, packet_buffer_list, trace_info, delay_list, iteration,
              mahimahi_results, fig_folder):
    tools.clear_folder(fig_folder)
    print('Parse Area...')
    area_dict = {}
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            standard_bw = int(link_trace.split('-')[0])
            for delay in delay_list:
                for delay_var in [f'{min(delay / 10, 20):.1f}']:
                    print('standard_bw:', standard_bw, 'delay:', delay,
                          'delay_var:', delay_var)
                    alg_dict = {}
                    stable_dict = {}
                    for iter_num in range(iteration):
                        # print('iter_num', iter_num)
                        for ccp_alg in ccp_algs:
                            log_name = f'{ccp_alg}-{link_trace}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                            stable_mark = stable_detect(
                                mahimahi_results[log_name]['time_list'],
                                mahimahi_results[log_name]['tput_list'], 0, 5,
                                delay * 10 / 1000, delay * 4 / 1000, 3, 0.06,
                                0.06)
                            area = calculate_area_detail(
                                mahimahi_results[log_name]['time_list'],
                                mahimahi_results[log_name]['tput_list'], 0,
                                stable_mark, standard_bw)
                            # print(log_name, stable_mark)
                            if ccp_alg not in alg_dict:
                                alg_dict[ccp_alg] = [area]
                                stable_dict[ccp_alg] = [
                                    mahimahi_results[log_name]['time_list']
                                    [stable_mark]
                                ]
                            else:
                                alg_dict[ccp_alg].append(area)
                                stable_dict[ccp_alg].append(
                                    mahimahi_results[log_name]['time_list']
                                    [stable_mark])
                            # print(f'{ccp_alg}: {area}', end=' ')
                        # print(' ')
                    area_dict[
                        f'{link_trace}-{packet_buffer}-{delay}-{delay_var}'] = {
                            'alg_dict': alg_dict,
                            'stable_dict': stable_dict
                        }
                    # print('\n')
    json.dump(
        area_dict,
        open(os.path.join(fig_folder, 'area_info.json'), 'w',
             encoding='utf-8'))

    print('Plot area...')
    for scenario in area_dict:
        plt.figure()
        for ccp_alg in area_dict[scenario]['alg_dict']:
            areas = area_dict[scenario]['alg_dict'][ccp_alg]
            mean = np.mean(areas)
            var = np.var(areas)
            plt.plot(areas, label=f'{ccp_alg}-{mean:.2f}-{var:.2f}')
        plt.title(scenario)
        plt.legend()
        plt.savefig(os.path.join(fig_folder, f'{scenario}-area.png'))
        plt.close()
    for scenario in area_dict:
        plt.figure()
        df = pd.DataFrame.from_dict(area_dict[scenario]['alg_dict'],
                                    orient='index').T
        df = df.drop(index=list(df.idxmax(axis=0)))
        sns.violinplot(data=df, palette='Set2')
        plt.title(scenario)
        plt.savefig(os.path.join(fig_folder, f'{scenario}-violin.png'))
        plt.close()
    return area_dict
