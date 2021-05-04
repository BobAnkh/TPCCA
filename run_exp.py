import subprocess
import time
from trace_generator import link_trace_generator

delay_list = [10, 25, 50, 100, 150, 200, 250]
bw_list = [(12, 0), (12, 1), (12, 2), (24, 0), (24, 1), (24, 2), (24, 4),(48, 0), (48, 1), (48, 2), (48, 4), (48, 8)]
length = 500
interval = 5

packet_buffer_list = [200]
log_folder = 'log'
duration = '60'
alg = 'ccp'

ccp_algs = {
    'bbr': './bbr/target/release/bbr',
    'copa': './copa/target/release/copa',
    'cubic': './generic-cong-avoid/target/release/cubic',
    'reno': './generic-cong-avoid/target/release/reno'
}

link_trace_generator(bw_list, length, interval)

iperf_server = subprocess.Popen('./run_iperf_server.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

for ccp_alg in ccp_algs:
    for packet_buffer in packet_buffer_list:
        for bw, var in bw_list:
            for delay in delay_list:
                for delay_var in [f'{min(delay / 10, 20):.1f}', f'{min(delay / 5, 30):.1f}']:
                    log_name = f'{ccp_alg}-{bw}-{var}-{delay}-{delay_var}'
                    print("RUN:", log_name)
                    ccp_args = ''
                    if ccp_alg == 'reno' or ccp_alg == 'cubic':
                        ccp_args = '--deficit_timeout=20'
                    cmd = f'sudo {ccp_algs[ccp_alg]} --ipc=netlink {ccp_args} > ./{log_folder}/{ccp_alg}-tmp.log 2> ./{log_folder}/{log_name}-ccp.log'
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                    subprocess.run("sudo dd if=/dev/null of=/proc/net/tcpprobe 2> /dev/null", shell=True)
                    subprocess.run(f'sudo dd if=/proc/net/tcpprobe of="./{log_folder}/{ccp_alg}-tmp.log" 2> /dev/null &', shell=True)
                    time.sleep(1)

                    cmd = f'mm-link ./traces/{bw}-{var} ./traces/{bw}-{var} --uplink-queue=droptail --downlink-queue=droptail --uplink-queue-args="packets={packet_buffer}" --downlink-queue-args="packets={packet_buffer}" --uplink-log="./{log_folder}/{log_name}-mahimahi.log" -- ./run_iperf.sh {log_folder} {log_name} {alg} {duration} {delay}ms {delay_var}ms'
                    subprocess.run(cmd, shell=True)
                    time.sleep(1)

                    subprocess.run("sudo killall dd 2> /dev/null", shell=True)
                    subprocess.run(f'grep ":9001" "./{log_folder}/{ccp_alg}-tmp.log" > "./{log_folder}/{log_name}-tcpprobe.log"', shell=True)
                    subprocess.run(f'rm -f "./{log_folder}/{ccp_alg}-tmp.log"', shell=True)
                    subprocess.run('sudo killall reno cubic bbr copa 2> /dev/null', shell=True)
                    time.sleep(1)

print("All Done!")
time.sleep(5)
if iperf_server.poll() != 0:
    iperf_server.kill()
subprocess.run('sudo killall iperf 2> /dev/null', shell=True)
