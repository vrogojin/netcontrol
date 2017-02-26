#!/bin/bash

# get script path
TC_PATH="/home/kkazemi/anduril_samples/Code_NetControl/targetcontrol"

# export TC_PATH to have it available for other scripts
export TC_PATH

$TC_PATH/bin/target_control -g "@var1@" -t "@var2@" -o "@param1@" -C "@var3@" -H $TC_PATH/config/heuristics/controllable.txt -N 10

value1=`cat @param1@/ans_count*.txt`
echo "$value1" >> @optOut1@
value2=`cat @param1@/ans_details*.txt`
echo "$value2" >> @optOut2@