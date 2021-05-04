#!/bin/bash
tc qdisc "$1" dev "$2" root netem delay "$3" "$4"