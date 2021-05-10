import subprocess
import time
from trace_generator import link_trace_generator, link_trace_multibw_generator
from tqdm import tqdm

delay_list = [10, 25, 50, 100, 150, 200, 250]
# bw_list = [(12, 0), (12, 1), (12, 2), (24, 0), (24, 1), (24, 2), (24, 4),(48, 0), (48, 1), (48, 2), (48, 4), (48, 8)]
# length = 1000
# interval = 5

packet_buffer_list = [200]
log_folder = 'log'
alg = 'ccp'
trace_folder = 'traces'

ccp_algs = {
    'bbr': './bbr/target/release/bbr',
    'copa': './copa/target/release/copa',
    'cubic': './generic-cong-avoid/target/release/cubic',
    'reno': './generic-cong-avoid/target/release/reno'
}

configs_list = [[(12, 4, 600, 5)], [(48, 12, 600, 5)], [(24, 4, 300, 5), (48, 8, 300, 5)]]
# link_trace_generator(bw_list, length, interval)
trace_info = link_trace_multibw_generator(configs_list, trace_folder)

print('Running iperf server...')
iperf_server = subprocess.Popen('./run_iperf_server.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

pbar = tqdm(total=len(ccp_algs)*len(packet_buffer_list)*len(trace_info)*len(delay_list)*2)
for ccp_alg in ccp_algs:
    for packet_buffer in packet_buffer_list:
        for link_trace in trace_info:
            for delay in delay_list:
                for delay_var in [f'{min(delay / 10, 20):.1f}', f'{min(delay / 5, 30):.1f}']:
                    pbar.update(1)
                    log_name = f'{ccp_alg}-{link_trace}-{delay}-{delay_var}'
                    print("RUN:", log_name)
                    duration = '120'
                    # if int(duration) * 2 < delay:
                    #     duration = str(int(delay / 2))
                    ccp_args = ''
                    if ccp_alg == 'reno' or ccp_alg == 'cubic':
                        ccp_args = '--deficit_timeout=20'
                    cmd = f'sudo {ccp_algs[ccp_alg]} --ipc=netlink {ccp_args} > ./{log_folder}/{ccp_alg}-tmp.log 2> ./{log_folder}/{log_name}-ccp.log'
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                    subprocess.run("sudo dd if=/dev/null of=/sys/kernel/debug/tracing/trace 2> /dev/null", shell=True)
                    subprocess.run("sudo sh -c 'echo 1 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable'", shell=True)
                    
                    time.sleep(0.5)

                    cmd = f'mm-link ./traces/{link_trace} ./traces/{link_trace} --uplink-queue=droptail --downlink-queue=droptail --uplink-queue-args="packets={packet_buffer}" --downlink-queue-args="packets={packet_buffer}" --uplink-log="./{log_folder}/{log_name}-mahimahi.log" -- ./run_iperf.sh {log_folder} {log_name} {alg} {duration} {delay}ms {delay_var}ms'
                    subprocess.run(cmd, shell=True)
                    time.sleep(1)
                    subprocess.run("sudo sh -c 'echo 0 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable'", shell=True)
                    subprocess.run(f'sudo dd if=/sys/kernel/debug/tracing/trace of="./{log_folder}/{ccp_alg}-tmp.log" 2> /dev/null', shell=True)
                    subprocess.run("sudo killall dd 2> /dev/null", shell=True)
                    subprocess.run(f'head -n 11 "./{log_folder}/{ccp_alg}-tmp.log" > "./{log_folder}/{log_name}-tcpprobe.log"', shell=True)
                    subprocess.run(f'grep ":9001" "./{log_folder}/{ccp_alg}-tmp.log" >> "./{log_folder}/{log_name}-tcpprobe.log"', shell=True)
                    subprocess.run(f'rm -f "./{log_folder}/{ccp_alg}-tmp.log"', shell=True)
                    subprocess.run('sudo killall reno cubic bbr copa 2> /dev/null', shell=True)
                    time.sleep(0.5)

pbar.close()
print("All Done!")
time.sleep(2)
print('Killall iperf...')
if iperf_server.poll() != 0:
    iperf_server.kill()
subprocess.run('sudo killall iperf 2> /dev/null', shell=True)
print('Finish all exps!')
