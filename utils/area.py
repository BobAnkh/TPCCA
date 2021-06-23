import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from utils import parseTputDelay, tools


def calculate_area_detail(time_list, tput_list, start_time_seq, end_time_seq,
                          standard_bw):
    '''
    Calculate area between throughput and standard bandwidth from start time to end time.

    Args:
        time_list (list): the whole time sequence
        tput_list (list): the whole throughput sequence corresponding to the time_list
        start_time_seq (int or float): start time sequence number
        end_time_seq (int or float): end time sequence number
        standard_bw (int or float): standard bandwidth

    Returns:
        float: area normalized by reaction time
    '''
    area_sum = 0
    for i, t in enumerate(time_list):
        if i < start_time_seq:
            continue
        if i >= end_time_seq:
            break
        area_sum = area_sum + abs(standard_bw -
                                  tput_list[i]) * (time_list[i + 1] - t)
    # TODO: may not normalize area by reaction time
    return area_sum / (time_list[end_time_seq] - time_list[start_time_seq])


def wnd_detect(time_list, start_wnd_time, start_wnd_seq, end_time, wnd_size):
    '''
    Search a best match point of the window end from the time sequence.

    Args:
        time_list (list): the whole time sequence
        start_wnd_time (int or float): window start time
        start_wnd_seq (int): window start time sequence number in time_list
        end_time (int or float): end time
        wnd_size (int or float): window size in milleseconds

    Returns:
        float, int, int: end time of the window, end time sequence number of the window, error code
    '''
    end_wnd_time = -1
    end_wnd_seq = -1
    error = -1
    if time_list[start_wnd_seq] != start_wnd_time:
        return end_wnd_time, end_wnd_seq, error - 2
    for ii, tt in enumerate(time_list[start_wnd_seq:]):
        if tt >= end_time:
            return end_wnd_time, end_wnd_seq, error - 1
        if tt >= start_wnd_time + wnd_size:
            end_wnd_time = tt
            end_wnd_seq = ii + start_wnd_seq
            error = 0
            return end_wnd_time, end_wnd_seq, error
    return end_wnd_time, end_wnd_seq, error


def stable_detect(time_list, tput_list, start_time, end_time, wnd_size,
                  move_size, wnd_num, mean_oscillation, var_oscillation):
    '''
    Detect when the CCA enters steady state.

    Args:
        time_list (list): the whole time sequence
        tput_list (list): the whole throughput sequence corresponding to the time_list
        start_time (int or float): start time
        end_time (int or float): end time
        wnd_size (int or float): window size in milleseconds
        move_size (int or float): time interval in milleseconds between adjacent two windows' start time
        wnd_num (int): how much windows are used in stable detection
        mean_oscillation (float): oscillation extent of means of windows
        var_oscillation (float): oscillation extent of vars of windows

    Returns:
        int: sequence number in time list of the point entering steady state
    '''
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
                # here we use the middle of windows, but we may can use the front of the windows
                # TODO: use the front of the windows as the stable point
                stable_mark = int((start_seq + end_seq) / 2)
        wnd_list = np.array(wnd_list)
        # print(np.var(wnd_list[:, 0]) , np.var(wnd_list[:, 1]))
        if np.var(wnd_list[:, 0]) <= mean_oscillation and np.var(
                wnd_list[:, 1]) <= var_oscillation:
            return stable_mark


def plot_area(ccp_algs, packet_buffer_list, trace_info, delay_list, iteration,
              mahimahi_results, fig_folder, name_map):
    '''
    Calculate area and plot figures.

    Args:
        ccp_algs (dict): CCP algorithms dict
        packet_buffer_list (list): packet buffer list
        trace_info (dict): traces information
        delay_list (list): delay list
        iteration (int): number of iterations
        mahimahi_results (dict): parsed mahimahi log
        fig_folder (str): folder to save figures
        name_map (dict): map ccp algorithm's name to actual CCA's name

    Returns:
        dict: area info
    '''
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
                            log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                            # TODO: may update stable detect params config
                            stable_mark = stable_detect(
                                mahimahi_results[log_name]['time_list'],
                                mahimahi_results[log_name]['tput_list'], 0, 40,
                                delay * 20 / 1000, delay * 8 / 1000, 3, 0.02,
                                0.02)
                            # TODO: normalize by bandwidth
                            area = calculate_area_detail(
                                mahimahi_results[log_name]['time_list'],
                                mahimahi_results[log_name]['tput_list'], 0,
                                stable_mark, standard_bw) / (standard_bw / 12)
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
                    area_dict[
                        f'{link_trace}-{packet_buffer}-{delay}-{delay_var}'] = {
                            'alg_dict': alg_dict,
                            'stable_dict': stable_dict
                        }
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
        plt.figure(figsize=(6.4, 3))
        df = pd.DataFrame.from_dict(area_dict[scenario]['alg_dict'],
                                    orient='index').T
        df = df.drop(index=list(df.idxmax(axis=0)))
        df.columns = [name_map[x] for x in df.columns]

        b = sns.violinplot(data=df, palette='Set2')
        print(plt.yticks())
        _, xlabels = plt.xticks()
        b.set_yticklabels(b.get_yticks(), size=20)
        b.set_xticklabels(xlabels, size=20)
        # plt.title(scenario)
        plt.ylabel('Area', fontsize='20')
        plt.savefig(os.path.join(fig_folder, f'{scenario}-violin.pdf'),
                    bbox_inches='tight')
        plt.close()
    return area_dict
