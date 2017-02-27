#!/bin/bash

echo	$SESSION_ID >> ../../sessions.txt

cat ../../result_page_template_header.html > result.html
echo "<em>SESSION: $SESSION_ID<br/>" >> result.html
echo "Please wait!</br>" >> result.html
echo "Analyzing the network ...<br/>" >> result.html
echo "<br/>" >> result.html
echo "The pipeline is doing its best to deliver the results to you ASAP. This computation may take loooong time<br/></em>" >> result.html
cat ../../result_page_template_footer.html >> result.html

echo $SESSION_ID > session_id
echo $SERVER_DIR > server_dir

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontend "mkdir -p $SERVER_DIR/" &&
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -r result.html frontend:$SERVER_DIR

screen -d -m -S "net_control_$SESSION_ID" ../../run_net_control.sh
#../../run_net_control.sh
#screen -m -S "net_control_$SESSION_ID" ../../run_net_control.sh
#../../run_net_control.sh &!