#!/bin/bash
sudo ./utils/set_tc.sh add ingress $5 $6
iperf -c $MAHIMAHI_BASE -p 9001 -Z $3 -t $4 -i 1 >"./$1/$2-iperf.log"
sudo ./utils/set_tc.sh del ingress $5 $6
sleep 1
