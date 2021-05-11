#!/bin/bash
# set -xeu

mk_folder() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo "Create folder $1"
    fi
}

echo 'Create new folders if not exsit...'
mk_folder traces
mk_folder log
mk_folder tmp
mk_folder figures/ccp
mk_folder figures/mahimahi

# install rust
if command -v rustc >/dev/null 2>&1; then
    echo 'Exists rustc...skip intstall!'
else
    echo 'No exists rustc...install rust!'
    curl https://sh.rustup.rs -sSf | sh -s
fi

echo 'Update git submodule...'
git submodule update --init --recursive

# reset everything
echo 'Reset...'
sudo pkill -9 iperf
sudo sh -c 'echo 0 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable'
sudo dd if=/dev/null of=/sys/kernel/debug/tracing/trace 2>/dev/null
sudo ./ccp-kernel/ccp_kernel_unload
# sudo modprobe -r tcp_probe
sudo modprobe tcp_bbr
# sudo modprobe tcp_probe port=9001
sudo sysctl -w net.ipv4.ip_forward=1

echo 'Make ccp-kernel...'
cd ccp-kernel && make >../tmp/build_tmp 2>../tmp/build_tmp
if [ $? -ne 0 ]; then
    cat ../$2/build_tmp
    exit 1
else
    #rm $2/build_tmp
    echo "Load ccp-kernel..."
    ulimit -Sn 8192
    echo $PWD
    sudo ./ccp_kernel_load ipc=0
    cd ..
fi

echo 'Make Congestion Control Algorithms...'
echo 'Build bbr...'
cd bbr && cargo build --release >../tmp/build_tmp 2>../tmp/build_tmp
if [ $? -ne 0 ]; then
    cat ../$2/build_tmp
    exit 1
else
    #rm $2/build_tmp
    cd ..
fi
echo 'Build copa...'
cd copa && cargo build --release >../tmp/build_tmp 2>../tmp/build_tmp
if [ $? -ne 0 ]; then
    cat ../$2/build_tmp
    exit 1
else
    #rm $2/build_tmp
    cd ..
fi
echo 'Build cubic and reno...'
cd generic-cong-avoid && cargo build --release >../tmp/build_tmp 2>../tmp/build_tmp
if [ $? -ne 0 ]; then
    cat ../$2/build_tmp
    exit 1
else
    #rm $2/build_tmp
    cd ..
fi

echo 'Build mahimahi...'
cd mahimahi && ./autogen.sh && ./configure && make && sudo make install

echo 'Chmod +x to some scripts...'
chmod +x run_iperf.sh
chmod +x run_iperf_server.sh
chmod +x run_tc.sh

echo 'Install Python dependencies...'
pip install requirements.txt

echo 'Setup done!'
