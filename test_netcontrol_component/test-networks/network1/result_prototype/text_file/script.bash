set -e
source /usr/share/anduril/bash/functions.sh "/home/kkazemi/test_netcontrol_component/test-networks/network1/result_prototype/text_file/_command"

#!/bin/bash

infile="/home/kkazemi/test_netcontrol_component/test-networks/network1/result_prototype/fil_case_both/csv.csv"

while read line
do
  temp="${line%\"}"
  temp="${temp#\"}"
  echo $temp >> "/home/kkazemi/test_netcontrol_component/test-networks/network1/result_prototype/text_file/optOut1.txt"
done < $infile