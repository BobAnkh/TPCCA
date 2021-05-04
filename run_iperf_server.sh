#!/bin/bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
iperf -s -p 9001 > ./log/iperf_server.log
