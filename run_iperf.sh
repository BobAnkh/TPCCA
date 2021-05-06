#!/bin/bash
sudo ./run_tc.sh add ingress $5 $6
iperf -c $MAHIMAHI_BASE -p 9001 -Z $3 -t $4 -i 1 >"./$1/$2-iperf.log"
sleep 1
sudo ./run_tc.sh del ingress $5 $6
sleep 1
