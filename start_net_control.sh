#!/bin/bash

echo	$SESSION_ID >> ../../sessions.txt

cat ../../result_page_template_header.html | sed "s/###/$SESSION_ID/g" > result.html
echo "<em>SESSION: $SESSION_ID<br/>" >> result.html
echo "Please wait!</br>" >> result.html
echo "<img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"48px\" height=\"47px\"><br>" >> result.html
echo "Analyzing the network ...<br/>" >> result.html
echo "<br/>" >> result.html
echo "The pipeline is doing its best to deliver the results to you ASAP. This computation may take loooong time<br/></em>" >> result.html
cat ../../result_page_template_footer.html >> result.html

echo "<?php \$output=shell_exec(\"ssh -i ../id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' net_control@backend \\\"echo STOP > /home/net_control/net_control/$SESSION_ID/control.txt\\\" 2>&1\"); ?>" > session_control.php
echo "<html>" >> session_control.php
echo "	<head>" >> session_control.php
echo "		<title>HALTING THE PIPELINE...</title>" >> session_control.php
echo "<META http-equiv=\"refresh\" content=\"5;result.html\">" >> session_control.php
echo "	</head>" >> session_control.php
echo "	<body>" >> session_control.php
echo "		<h1>HALTING THE PIPELINE...</h1>" >> session_control.php
echo "	</body>" >> session_control.php
echo "</html>" >> session_control.php

echo $SESSION_ID > session_id
echo $SERVER_DIR > server_dir
echo $SERVER_URL > server_url

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontend "mkdir -p $SERVER_DIR/" &&
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -r result.html session_control.php frontend:$SERVER_DIR

screen -d -m -S "net_control_$SESSION_ID" ../../run_net_control.sh
#../../run_net_control.sh
#screen -m -S "net_control_$SESSION_ID" ../../run_net_control.sh
#../../run_net_control.sh &!