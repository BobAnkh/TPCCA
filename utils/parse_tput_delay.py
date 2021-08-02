#!/usr/bin/python3

import os
import subprocess

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from utils import tools

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def get_throughput_data(fn):
    cmd = "grep ' + ' {} | awk '{{print $1, $3}}'".format(fn)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    cmd2 = "grep '# base timestamp' {} | awk '{{print $4}}'".format(fn)
    bt = subprocess.run(cmd2, stdout=subprocess.PIPE, shell=True)
    bt = bt.stdout.decode("utf-8").split('\n')[0]
    for l in res.stdout.decode("utf-8").split('\n'):
        sp = l.split(" ")
        if len(sp) != 2:
            continue
        t, v = sp
        yield float(int(t) - int(bt)) / 1e3, float(v)


def get_delay_data(fn):
    cmd = "grep ' - ' {} | awk '{{print $1, $5}}'".format(fn)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    cmd2 = "grep '# base timestamp' {} | awk '{{print $4}}'".format(fn)
    bt = subprocess.run(cmd2, stdout=subprocess.PIPE, shell=True)
    bt = bt.stdout.decode("utf-8").split('\n')[0]
    for l in res.stdout.decode("utf-8").split('\n'):
        sp = l.split(" ")
        if len(sp) != 2:
            continue
        t, v = sp
        yield float(int(t) - int(bt)) / 1e3, float(v)


def get_throughput(data, start_time, end_time, binsize=0):
    bin_start = start_time
    last_t = start_time
    current_bin_tput = 0
    for t, p in data:
        if t < start_time:
            continue
        if t > end_time:
            break
        if t > (bin_start + binsize):  # start new bin
            yield bin_start, current_bin_tput / (t - bin_start)
            bin_start = t
            current_bin_tput = p * 8.0
        else:
            current_bin_tput += p * 8.0
            last_t = t


def get_delays(data, bin_times):
    # this function is not used but left here in case to be used
    next_bin = next(bin_times)
    delays = []
    for t, p in data:
        if t < next_bin:
            delays.append(p)
        else:
            if len(delays) > 0:
                yield np.mean(delays)
            else:
                yield 0
            delays = []
            delays.append(p)
            next_bin = next(bin_times)

    yield np.mean(delays)


def get_times(fn, binsize):
    bin_start = 0
    yield 0
    for t, _ in get_throughput_data(fn):
        if (bin_start + binsize) > t:
            yield t
    yield t


def get_expt_data(fn, duration, binsize=0):
    tp = get_throughput_data(fn)
    td = get_delay_data(fn)
    ts, tp = zip(*get_throughput(tp, 0, duration, binsize))
    ts = list(ts)
    dl = get_delays(td, iter(ts))
    return zip(ts, tp, dl)


# filename: <alg>-<bw>-<bw_scenario>-<delay>-<delay_var>-mahimahi.log
def binAlgs(fns):
    '''
    Parse filename.

    Args:
        fns (list): each element is a file name. <alg>-<bw>-<bw_scenario>-<delay>-<delay_var>-mahimahi.log

    Returns:
        dict: file infos
    '''
    plots = {}
    for fn in fns:
        sp = fn.split('-')
        if sp[-1] != "mahimahi.log":
            continue
        alg, bw, bw_seq, packet_buf, delay, delay_var, iter_num = sp[:-1]
        pl = (alg, bw, bw_seq, packet_buf, delay, delay_var, iter_num)
        if pl in plots:
            plots[pl].append(fn)
        else:
            plots[pl] = [fn]
    return plots


def parse_tput_delay(log_folder, duration, binsize=0):
    '''
    Parse throughput and delay. (delay is not used yet)

    Args:
        log_folder (str): folder of raw logs
        duration (int or float): duration of time sequence
        binsize (int, optional): binsize of throughput time interval. Defaults to 0.

    Returns:
        dict: time sequence, throughput sequence and delay sequence of log files.
    '''
    exps = binAlgs(sorted(os.listdir(log_folder)))
    results = {}

    print('Parse Throughput and Delay...')
    for exp in tqdm(exps):
        time_list = []
        tput_list = []
        dl_list = []
        for t, tput, dl in get_expt_data(
                os.path.join(log_folder, exps[exp][0]),
                min(duration, 2 * float(exp[4])),
                int(exp[4]) * 2 / 1000 * int(exp[1]) / 12):
            time_list.append(t)
            tput_list.append(tput / 1000 / 1000)
            dl_list.append(dl)
        results[exps[exp][0]] = {
            'time_list': time_list,
            "tput_list": tput_list,
            "dl_list": dl_list
        }
    return results


def plot_tput_delay(ccp_algs,
                    packet_buffer_list,
                    trace_info,
                    delay_list,
                    iteration,
                    mahimahi_results,
                    fig_folder,
                    enable_alg_plot=False,
                    enable_iteration_plot=False):
    '''
    Plot throughput and delay(delay plot not implemented yet).

    Args:
        ccp_algs (dict): CCP algorithms dict
        packet_buffer_list (list): packet buffer list
        trace_info (dict): traces information
        delay_list (list): delay list
        iteration (int): number of iterations
        mahimahi_results (dict): parsed mahimahi log
        fig_folder (str): folder to save figures
        enable_alg_plot (bool, optional): if plot every algorithm. Defaults to False.
        enable_iteration_plot (bool, optional): if plot every iteration. Defaults to False.
    '''
    tools.clear_folder(fig_folder)
    print('Plot Throughput and Delay...')
    if enable_alg_plot:
        for res in tqdm(mahimahi_results):
            plt.figure(figsize=(6.4, 3))
            plt.plot(mahimahi_results[res]['time_list'],
                     mahimahi_results[res]['tput_list'],
                     'ro-',
                     label='Throughput')
            # plt.title(res)
            plt.xlabel('Time (s)', fontsize='12')
            plt.ylabel('Throughput (Mbps)', fontsize='12')
            plt.legend()
            plt.savefig(os.path.join(fig_folder, res[:-4] + '.png'),
                        bbox_inches='tight')
            plt.close()
    pbar = tqdm(total=len(packet_buffer_list) * len(trace_info) *
                len(delay_list) * iteration)
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                for iter_num in range(iteration):
                    plt.figure(figsize=(6.4, 3))
                    for ccp_alg in ccp_algs:
                        log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                        plt.plot(
                            mahimahi_results[log_name]['time_list'][0:60],
                            mahimahi_results[log_name]['tput_list'][0:60],
                            label=f'{ccp_alg}')
                    # plt.title(f'{link_trace}-{delay}-{delay_var}-mahimahi')
                    plt.xlabel('Time (s)', fontsize='12')
                    plt.ylabel('Throughput (Mbps)', fontsize='12')
                    plt.legend()
                    plt.savefig(os.path.join(
                        fig_folder,
                        f'diff-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}-mahimahi.png'
                    ),
                                bbox_inches='tight')
                    plt.close()
                    pbar.update(1)
    pbar.close()
    if iteration > 1 and enable_iteration_plot:
        pbar = tqdm(total=len(packet_buffer_list) * len(trace_info) *
                    len(delay_list) * iteration)
        for packet_buffer in packet_buffer_list:
            for link_trace in trace_info:
                for delay, delay_var in delay_list:
                    delay = int(delay)
                    delay_var = round(delay_var, 1)
                    for ccp_alg in ccp_algs:
                        plt.figure(figsize=(6.4, 3))
                        for iter_num in range(iteration):
                            log_name = f'{ccp_alg}-{link_trace}-{delay}-{delay_var}-{iter_num}-mahimahi.log'
                            plt.plot(
                                mahimahi_results[log_name]['time_list'],
                                mahimahi_results[log_name]['tput_list'],
                                label=f'{iter_num}')
                        # plt.title(f'{ccp_alg}-{link_trace}-{delay}-{delay_var}-mahimahi')
                        plt.xlabel('Time (s)', fontsize='12')
                        plt.ylabel('Throughput (Mbps)', fontsize='12')
                        plt.legend()
                        plt.savefig(os.path.join(
                            fig_folder,
                            f'iter-{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-mahimahi.png'
                        ),
                                    bbox_inches='tight')
                        plt.close()
                        pbar.update(1)
        pbar.close()
