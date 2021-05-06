#!/bin/bash
echo '[INFO] Start iperf server. Listen port 9001...'
iperf -s -p 9001 >./log/iperf_server.log
