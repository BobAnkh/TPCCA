import json
import os

from utils.ccp_parse import bbr_parse

delay_list = [10, 25, 50, 100, 150, 200, 250]

packet_buffer_list = [200]
log_folder = 'log'
fig_folder = 'figures'
trace_folder = 'traces'
ccp_folder = 'ccp'

ccp_algs = {
    'bbr': './bbr/target/release/bbr',
    'copa': './copa/target/release/copa',
    'cubic': './generic-cong-avoid/target/release/cubic',
    'reno': './generic-cong-avoid/target/release/reno'
}

trace_info = json.load(
    open(os.path.join(trace_folder, 'trace_info.json'), encoding='utf-8'))

bbr_parse(trace_info, delay_list, log_folder,
          os.path.join(fig_folder, ccp_folder))
