#!/bin/bash
# set -xeu

mk_folder(){
    if [ ! -d "$1" ]; then
    mkdir "$1"
    echo "Create folder $1"
fi
}

echo 'Create new folders if not exsit...'
mk_folder traces
mk_folder log
mk_folder tmp

# install rust
if command -v rustc >/dev/null 2>&1; then 
    echo 'Exists rustc...skip intstall!' 
else 
    echo 'No exists rustc...install rust!'
    curl https://sh.rustup.rs -sSf | sh -s
fi

echo 'Update git submodule...'
git submodule update --init --recursive
echo 'Make ccp-kernel'
cd ccp-kernel && make
sudo ./ccp_kernel_load ipc=0

echo 'Make Congestion Control Algorithms...'
cd ..
cd bbr && cargo build --release && cd ..
cd copa && cargo build --release && cd ..
cd generic-cong-avoid && cargo build --release && cd ..

echo 'Chmod +x to some scripts'
chmod +x run_iperf.sh
chmod +x run_iperf_server.sh
chmod +x run_tc.sh

echo 'Setup done!'