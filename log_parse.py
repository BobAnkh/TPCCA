import json
import os

import toml

from utils.ccp_parse import bbr_parse
from utils.parseTputDelay import parse_tput_delay, plot_tput_delay

configs = toml.load('config.toml')

delay_list = configs['data']['delay_list']

packet_buffer_list = configs['data']['packet_buffer_list']
log_folder = configs['path']['log_folder']
fig_folder = configs['path']['fig_folder']
trace_folder = configs['path']['trace_folder']
ccp_fig_folder = configs['path']['ccp_fig_folder']
mahimahi_fig_folder = configs['path']['mahimahi_fig_folder']
binsize = configs['data']['log']['binsize']
duration = configs['data']['log']['duration']

ccp_algs = configs['data']['ccp_algs']

trace_info = json.load(
    open(os.path.join(trace_folder, 'trace_info.json'), encoding='utf-8'))

bbr_parse(trace_info, delay_list, log_folder,
          os.path.join(fig_folder, ccp_fig_folder))

plot_tput_delay(ccp_algs, packet_buffer_list, trace_info, delay_list, log_folder, os.path.join(fig_folder, mahimahi_fig_folder), duration, binsize)
