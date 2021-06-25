import json
import os

import toml

from utils.area import plot_area
from utils.ccp_parse import bbr_parse
from utils.parseTputDelay import parse_tput_delay, plot_tput_delay

configs = toml.load('config.toml')

delay_list = configs['data']['delay_list']
packet_buffer_list = configs['data']['packet_buffer_list']
iteration = configs['data']['iteration']
name_map = configs['data']['plot_name_map']
ccp_algs = configs['data']['ccp_algs']

log_folder = configs['path']['log_folder']
fig_folder = configs['path']['fig_folder']
trace_folder = configs['path']['trace_folder']
ccp_fig_folder = configs['path']['ccp_fig_folder']
mahimahi_fig_folder = configs['path']['mahimahi_fig_folder']
area_fig_folder = configs['path']['area_fig_folder']

binsize = configs['data']['log']['binsize']
duration = configs['data']['log']['duration']
enable_iteration_plot = configs['data']['log']['enable_iteration_plot']
enable_alg_plot = configs['data']['log']['enable_alg_plot']

trace_info = json.load(
    open(os.path.join(trace_folder, 'trace_info.json'), encoding='utf-8'))

print('parse bbr ccp log')
bbr_parse(trace_info, delay_list, iteration, log_folder,
          os.path.join(fig_folder, ccp_fig_folder))

print('parse mahimahi log')
mahimahi_results = parse_tput_delay(log_folder, duration, binsize)
json.dump(mahimahi_results,
          open('tmp/mahimahi_results.json', 'w', encoding='utf-8'))
# mahimahi_results = json.load(open('tmp/mahimahi_results.json'))

print('plot throughput and delay')
plot_tput_delay(ccp_algs, packet_buffer_list, trace_info, delay_list,
                iteration, mahimahi_results,
                os.path.join(fig_folder, mahimahi_fig_folder), enable_alg_plot,
                enable_iteration_plot)

print('parse mahimahi log and ')
area_dict = plot_area(ccp_algs, packet_buffer_list, trace_info, delay_list,
                      iteration, mahimahi_results,
                      os.path.join(fig_folder, area_fig_folder), name_map)
