import json
import subprocess
import sys
import time

import toml
from tqdm import tqdm

from trace_generator import link_trace_multibw_generator
from utils import arg_parser
from utils.tools import makefolder, clear_folder

IPERF_PORT = 9001

args = arg_parser.argument_parser()
config_file_path = args.config
configs = toml.load(config_file_path)

enable_tcp_probe = configs['main']['enable_tcp_probe']
delay_emulator = configs['main']['delay_emulator']

delay_list = configs['data']['delay_list']
packet_buffer_list = configs['data']['packet_buffer_list']
alg = configs['data']['alg']
ccp_algs = configs['data']['ccp_algs']
exp_duration = configs['data']['exp_duration']

trace_folder = configs['path']['trace_folder']
log_folder = configs['path']['log_folder']

trace_list = configs['data']['trace_list']
iteration = configs['data']['iteration']

makefolder(trace_folder)
makefolder(log_folder)

trace_info = link_trace_multibw_generator(trace_list, trace_folder)
# trace_info = json.load(
#     open(os.path.join(trace_folder, 'trace_info.json'), encoding='utf-8'))
clear_folder(log_folder)

print('Running iperf server...')
iperf_server = subprocess.Popen(f'iperf -s -p {IPERF_PORT} >./{log_folder}/iperf_server.log',
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                encoding="utf-8")

pbar = tqdm(total=len(ccp_algs) * len(packet_buffer_list) * len(trace_info) *
            len(delay_list) * iteration)
for ccp_alg in ccp_algs:
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay, delay_var in delay_list:
                delay = int(delay)
                delay_var = round(delay_var, 1)
                for iter_num in range(iteration):
                    pbar.update(1)
                    log_name = f'{ccp_alg}-{link_trace}-{packet_buffer}-{delay}-{delay_var}-{iter_num}'
                    print("RUN:", log_name)
                    # duration = trace_info[link_trace]['length']
                    duration = exp_duration
                    # if int(duration) * 2 < delay:
                    #     duration = str(int(delay / 2))
                    ccp_args = ''
                    # if ccp_alg == 'reno' or ccp_alg == 'cubic':
                    #     ccp_args = '--deficit_timeout=20'
                    cmd = f'sudo {ccp_algs[ccp_alg]} --ipc=netlink {ccp_args} > ./{log_folder}/{ccp_alg}-tmp.log 2> ./{log_folder}/{log_name}-ccp.log'
                    subprocess.Popen(cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     encoding="utf-8")

                    if enable_tcp_probe:
                        subprocess.run(
                            "sudo dd if=/dev/null of=/sys/kernel/debug/tracing/trace 2> /dev/null",
                            shell=True)
                        subprocess.run(
                            "sudo sh -c 'echo 1 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable'",
                            shell=True)
                        time.sleep(0.1)

                    if delay_emulator == 'mahimahi':
                        cmd = f'mm-delay {delay} mm-link ./traces/{link_trace} ./traces/{link_trace} --uplink-queue=droptail --downlink-queue=droptail --uplink-queue-args="packets={packet_buffer}" --downlink-queue-args="packets={packet_buffer}" --uplink-log="./{log_folder}/{log_name}-mahimahi.log" -- ./run_iperf_mmdelay.sh {log_folder} {log_name} {alg} {duration} {IPERF_PORT}'
                    elif delay_emulator == 'tc':
                        cmd = f'mm-link ./traces/{link_trace} ./traces/{link_trace} --uplink-queue=droptail --downlink-queue=droptail --uplink-queue-args="packets={packet_buffer}" --downlink-queue-args="packets={packet_buffer}" --uplink-log="./{log_folder}/{log_name}-mahimahi.log" -- ./run_iperf_tc.sh {log_folder} {log_name} {alg} {duration} {IPERF_PORT} {delay * 2}ms {delay_var * 2}ms'
                    else:
                        sys.exit("Wrong delay emulator! Check your config!")
                    subprocess.run(cmd, shell=True)

                    if enable_tcp_probe:
                        time.sleep(0.1)
                        subprocess.run(
                            "sudo sh -c 'echo 0 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable'",
                            shell=True)
                        subprocess.run(
                            f'sudo dd if=/sys/kernel/debug/tracing/trace of="./{log_folder}/{ccp_alg}-tmp.log" 2> /dev/null',
                            shell=True)
                        subprocess.run("sudo killall dd 2> /dev/null",
                                       shell=True)
                        subprocess.run(
                            f'head -n 11 "./{log_folder}/{ccp_alg}-tmp.log" > "./{log_folder}/{log_name}-tcpprobe.log"',
                            shell=True)
                        subprocess.run(
                            f'grep ":{IPERF_PORT}" "./{log_folder}/{ccp_alg}-tmp.log" >> "./{log_folder}/{log_name}-tcpprobe.log"',
                            shell=True)
                        subprocess.run(
                            f'rm -f "./{log_folder}/{ccp_alg}-tmp.log"',
                            shell=True)

                    subprocess.run(
                        'sudo killall reno cubic bbr copa 2> /dev/null',
                        shell=True)
                    time.sleep(0.2)

pbar.close()
print("All Done!")
time.sleep(2)
print('Killall iperf...')
if iperf_server.poll() != 0:
    iperf_server.kill()
subprocess.run('sudo killall iperf 2> /dev/null', shell=True)
print('Finish all exps!')
