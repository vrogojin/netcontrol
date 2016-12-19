#!/bin/bash

echo	$SESSION_ID >> ../../sessions.txt

cat ../../result_page_template_header.html > result.html
echo "<em>SESSION: $SESSION_ID<br/>" >> result.html
echo "Please wait!</br>" >> result.html
echo "Analyzing the network ...<br/>" >> result.html
echo "<br/>" >> result.html
echo "You will be notified by email when the results of the analysis are ready<br/></em>" >> result.html
cat ../../result_page_template_footer.html >> result.html

echo $SESSION_ID > session_id
echo $SERVER_DIR > server_dir

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' webadmin@combio.abo.fi "mkdir -p $SERVER_DIR/" &&
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -r result.html webadmin@combio.abo.fi:$SERVER_DIR

screen -d -m -S "net_control_$SESSION_ID" ../../run_net_control.sh
#screen -m -S "net_control_$SESSION_ID" ../../run_net_control.sh
#../../run_net_control.sh &!