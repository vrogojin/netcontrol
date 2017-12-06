#!/bin/bash

## This script invokes data importing pipeline for FBL paper
## "Identifying central genes in gene networks by counting feedback loops"
## Invoking file get_data_for_ieee_paper.and

export SESSION_ID=$(cat session_id)
export SERVER_DIR=$(cat server_dir)
export SERVER_URL=$(cat server_url)
export USER_MAIL=$(cat useremail)

NL=$'\n'

export MOKSISKAAN_HOME=/opt/moksiskaan/db
#export EXEC_DIR=/home/vrogojin/biomedicum/FBL-paper-exec
#export VR_PIPELINES_HOME=/home/vrogojin/mercurial-reps/vrogojin/FBL-studies
#export BETA_BUNDLE=/home/vrogojin/anduril-svn/trunk/beta
source $MOKSISKAAN_HOME/pipeline/execInit.sh


if [ -e ../../server_url ]; then
    export SERVER_URL=$(cat ../../server_url)
fi

mkdir result
touch result.zip
touch result.html

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontend "mkdir -p $SERVER_DIR/result" &&

../../netco4biomed.and &
ID=$!


../../notification_sender.sh postmaster@combio.abo.fi $USER_MAIL "TASK $SESSION_ID STARTED" \
    "Hello,${NL}You have started task at NetControl4BioMed pipeline.${NL}Follow the progress of the analysis at $SERVER_URL/$SESSION_ID/result.html" 2>&1 > mail.log

echo "<html>" > pipeline.log.html
echo "<body>" >> pipeline.log.html
echo "<pre>" >> pipeline.log.html
echo "INITIALIZING..." >> pipeline.log.html
echo "</pre>" >> pipeline.log.html
echo "<a name=\"end\">&nbsp;</a>" >> pipeline.log.html
echo "</body>" >> pipeline.log.html
echo "</html>" >> pipeline.log.html

echo "<font color=orange>PIPELINE RUNNING...</font>" > status.txt
../../generate_result_page.sh
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' pipeline.log.html result.html frontend:$SERVER_DIR

result_not_ready=1

running=1
while [ $running -eq 1 ]; do
    sleep 5
    cp log_netco4biomed/_global pipeline.log
    echo "<html>" > pipeline.log.html
    echo "<body>" >> pipeline.log.html
    echo "<pre>" >> pipeline.log.html
    cat pipeline.log >> pipeline.log.html
    echo "</pre>" >> pipeline.log.html
    echo "<a name=\"end\">&nbsp;</a>" >> pipeline.log.html
    echo "</body>" >> pipeline.log.html
    echo "</html>" >> pipeline.log.html
    ../../generate_result_page.sh
    scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' pipeline.log.html pipeline.log result.html frontend:$SERVER_DIR
    if [ -e "network.graphml" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' network.graphml frontend:$SERVER_DIR/result
    fi
    if [ -e "network.pdf" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' network.pdf frontend:$SERVER_DIR/result
    fi
    if [ -e "legend.pdf" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' legend.pdf frontend:$SERVER_DIR/result
    fi
    if [ -e "network.txt" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' network.txt frontend:$SERVER_DIR/result
    fi
    if [ -e "result/details.txt" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' result/details.txt frontend:$SERVER_DIR/result
    fi
    if [ -e "result/driven.csv" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' result/driven.csv frontend:$SERVER_DIR/result
    fi
    if [ -e "result/extra.csv" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' result/extra.csv frontend:$SERVER_DIR/result
    fi
    if [ -e "result/network.graphml" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' result/network.graphml frontend:$SERVER_DIR/result
    fi
    if [ -s "result.zip" ]
    then
	scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' result.zip frontend:$SERVER_DIR
	if [ $result_not_ready -eq 1 ]; then
	    ../../notification_sender.sh postmaster@combio.abo.fi $USER_MAIL "TASK $SESSION_ID ALMOST COMPLETED." \
		"Hello,${NL}The results of your network control analysis are ready and available for download.${NL}The PDF plot with the network is being generated. Depending of the size of the network, this may take from a couple of minutes to many hours.${NL}If the network is too large, PDF generation may fail.${NL}For your convenience, visit $SERVER_URL/$SESSION_ID/result.html" 2>&1 > mail.log
	    result_not_ready=0
	fi
    fi
    if grep -q 'STOP' control.txt; then
	pkill --signal 9 -P "$ID"
	kill -9 "$ID"
	running=0
	echo "GOT TERM SIGNAL. TERMINATING $ID" > out.txt
    fi
    if grep -q 'Log closed' log_netco4biomed/_global; then
	running=0
    fi
done

echo "WAITING FOR $ID TO BE TERMINATED" >> out.txt
wait $ID
echo "$ID TERMINATED" >> out.txt

#   anduril run -d $EXEC_DIR -b $MOKSISKAAN_HOME/pipeline -b $ANDURIL_HOME/sequencing -b $ANDURIL_HOME/beta -threads 8 $VR_PIPELINES_HOME/get_data_for_ieee_paper.and $1 $2 $3 $4 $5 $6
#   tar -czf /home/vrogojin/biomedicum/FBL-paper-exec_$( date '+%Y_%m_%d' ).tar.gz $EXEC_DIR

cp log_netco4biomed/_global pipeline.log
#cat ../../result_page_template_header.html | sed "s/###/$SESSION_ID/g" | sed "s/<meta http-Equiv=\"Refresh\" Content=\"5\">//g" > result.html

ST="RUNNING"
if [ -s res ]
then
    echo "<font color=green>PIPELINE TERMINATRED. STATUS OK</font>" > status.txt
    ST="OK"
else
    if grep -q 'STOP' control.txt; then
	echo "<font color=red>PIPELINE INTERRUPTED BY USER. CHECK THE LOG</font>" > status.txt
	export ST="INTERRUPTED"
    else
	echo "<font color=red>PIPELINE FAILED. CHECK THE LOG</font>" > status.txt
	export ST="FAILED"
    fi
fi
../../generate_result_page.sh
sed -i 's/Refresh/---/g' result.html


ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontend "mkdir -p $SERVER_DIR/" &&
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -r result result.zip result.html pipeline.log frontend:$SERVER_DIR

#emailcommand="echo \"Results of the analysis for your query are ready for download. Please visit http://combio.abo.fi/web_services/remote_call/net_control/$SESSION_ID/result.html at your convenience\" | mail -s \"NetControl4BioMed: results $SESSION_ID\" $(cat useremail)"
#emailcommand="ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontent $emailcommand"
#eval '$emailcommand'

../../notification_sender.sh postmaster@combio.abo.fi $USER_MAIL "TASK $SESSION_ID COMPLETED. STATUS $ST" \
    "Hello,${NL}Your data analysis session completed.${NL}Status: ${ST}.${NL}For your convenience, visit $SERVER_URL/$SESSION_ID/result.html" 2>&1 > mail.log
