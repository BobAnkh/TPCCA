#!/bin/bash
sudo ./utils/set_tc.sh add ingress $6 $7
iperf -c $MAHIMAHI_BASE -p $5 -Z $3 -t $4 -i 1 >"./$1/$2-iperf.log"
sudo ./utils/set_tc.sh del ingress $6 $7
sleep 1
