#!/bin/bash
echo '[INFO] Start iperf server. Listen port 9001...'
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
iperf -s -p 9001 > ./log/iperf_server.log
