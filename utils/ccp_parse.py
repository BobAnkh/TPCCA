import os
import re

import matplotlib.pyplot as plt

from utils import tools


def bbr_parse(packet_buffer_list, trace_info, delay_list, iteration, log_folder, fig_folder):
    '''
    Parse bbr log of CCP

    Args:
        packet_buffer_list(list): packet buffer list
        trace_info (dict): traces information
        delay_list (list): delay list
        iteration (int): number of iterations
        log_folder (str): folder of logs
        fig_folder (str): folder to save figures
    '''
    tools.clear_folder(fig_folder)
    ccp_alg = 'bbr' #???
    header = r'[A-Za-z]{3}\s[0-9]{1,2}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,3}\sINFO\sconfigured\s(.+?),\sprobe_rtt_interval:\sDuration\s\{\ssecs:\s([0-9]+?),\snanos:\s([0-9]+?)\s\},\sipc:\s([A-Za-z]+)'
    probe_bw = r'[A-Za-z]{3}\s[0-9]{1,2}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,3}\sINFO\sprobe_bw,\sbottle\srate\s\(Mbps\):\s([0-9.]+?),\srate\s\(Mbps\):\s([0-9.]+?),\selapsed:\s([0-9.]+)'
    new_flow = r'[A-Za-z]{3}\s[0-9]{1,2}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,3}\sINFO\snew_flow'
    new_min_rtt = r'[A-Za-z]{3}\s[0-9]{1,2}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,3}\sINFO\snew\smin_rtt,\sbottle\srate:\s([0-9.]+?),\smin_rtt\s\(us\):\s([0-9]+)'
    switching = r'[A-Za-z]{3}\s[0-9]{1,2}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,3}\sINFO\sswitching\sto\sPROBE_BW,\smin\srtt\s\(us\):\s([0-9]+?),\sRate\s\(5\/4\):\s([0-9.]+?),\sbottle\srate\s\(Mbps\):\s([0-9.]+?),\sRate\s\(3\/4\):\s([0-9.]+?),\scwnd:\s([0-9.]+)'
    PROBE_BW = r'[A-Za-z]{3}\s[0-9]{1,2}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{1,3}\sINFO\sPROBE_BW:\supdating\srate,\sRate\s\(5\/4\):\s([0-9.]+?),\sbottle\srate:\s([0-9.]+?),\sRate\s\(3\/4\):\s([0-9.]+?),\scwnd:\s([0-9.]+)'

    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                for iter_num in range(iteration):
                    plt.figure()
                    bottle_rate = []
                    rate = []
                    elapsed_time = []
                    log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}'
                    with open(os.path.join(log_folder,
                                        log_name + '-ccp.log')) as f:
                        logs = f.readlines()
                        logs = list(map(lambda x: x.strip('\n'), logs))
                        for str in logs:
                            if re.match(header, str):
                                alg = re.match(header, str).group(1)
                                probe_rtt_interval_secs = re.match(
                                    header, str).group(2)
                                probe_rtt_interval_nanos = re.match(
                                    header, str).group(3)
                                # print(alg, probe_rtt_interval_secs, probe_rtt_interval_nanos)
                            if re.match(probe_bw, str):
                                probe_bw_brate = re.match(probe_bw,
                                                        str).group(1)
                                probe_bw_rate = re.match(probe_bw,
                                                        str).group(2)
                                probe_bw_elapsed = re.match(probe_bw,
                                                            str).group(3)
                                # print(probe_bw_brate, probe_bw_rate, probe_bw_elapsed)
                                bottle_rate.append(float(probe_bw_brate))
                                rate.append(float(probe_bw_rate))
                                elapsed_time.append(float(probe_bw_elapsed))
                            if re.match(new_flow, str):
                                continue
                            if re.match(new_min_rtt, str):
                                new_rtt_brate = re.match(new_min_rtt,
                                                        str).group(1)
                                new_rtt = re.match(new_min_rtt, str).group(2)
                            if re.match(switching, str):
                                switching_rtt = re.match(switching,
                                                        str).group(1)
                                switching_5rate = re.match(switching,
                                                        str).group(2)
                                switching_brate = re.match(switching,
                                                        str).group(3)
                                switching_3rate = re.match(switching,
                                                        str).group(4)
                                switching_cwnd = re.match(switching,
                                                        str).group(5)
                            if re.match(PROBE_BW, str):
                                PROBE_BW_5rate = re.match(PROBE_BW,
                                                        str).group(1)
                                PROBE_BW_brate = re.match(PROBE_BW,
                                                        str).group(2)
                                PROBE_BW_3rate = re.match(PROBE_BW,
                                                        str).group(3)
                                PROBE_BW_cwnd = re.match(PROBE_BW,
                                                        str).group(4)
                    plt.plot(elapsed_time, rate, 'ro-', label='Rate')
                    plt.plot(elapsed_time,
                            bottle_rate,
                            'b^-',
                            label='BottleRate')
                    plt.title(log_name)
                    plt.xlabel('Time (s)')
                    plt.ylabel('BandWidth (Mbps)')
                    plt.legend()
                    plt.savefig(os.path.join(fig_folder,
                                            log_name + '-ccp.png'))
                    plt.close()
