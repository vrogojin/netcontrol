#!/bin/bash

## This script invokes data importing pipeline for FBL paper
## "Identifying central genes in gene networks by counting feedback loops"
## Invoking file get_data_for_ieee_paper.and

export SESSION_ID=$(cat session_id)
export SERVER_DIR=$(cat server_dir)


export MOKSISKAAN_HOME=/opt/moksiskaan/db
#export EXEC_DIR=/home/vrogojin/biomedicum/FBL-paper-exec
#export VR_PIPELINES_HOME=/home/vrogojin/mercurial-reps/vrogojin/FBL-studies
#export BETA_BUNDLE=/home/vrogojin/anduril-svn/trunk/beta
source $MOKSISKAAN_HOME/pipeline/execInit.sh

mkdir result
touch result.zip
touch result.html

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontend "mkdir -p $SERVER_DIR/" &&

../../netco4biomed.and &
ID=$!

echo "<html>" > pipeline.log.html
echo "<body>" >> pipeline.log.html
echo "<pre>" >> pipeline.log.html
echo "INITIALIZING..." >> pipeline.log.html
echo "</pre>" >> pipeline.log.html
echo "<a name=\"end\">&nbsp;</a>" >> pipeline.log.html
echo "</body>" >> pipeline.log.html
echo "</html>" >> pipeline.log.html

status="PIPELINE RUNNING..."
../../generate_result_page.sh
sed -i "s/___STATUS___/$status/g" result.html
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' pipeline.log.html result.html frontend:$SERVER_DIR

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
    sed -i "s/___STATUS___/$status/g" result.html
    scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' pipeline.log.html pipeline.log result.html frontend:$SERVER_DIR
    if grep -q 'Log closed' log_netco4biomed/_global; then
	running=0
    fi
done

#   anduril run -d $EXEC_DIR -b $MOKSISKAAN_HOME/pipeline -b $ANDURIL_HOME/sequencing -b $ANDURIL_HOME/beta -threads 8 $VR_PIPELINES_HOME/get_data_for_ieee_paper.and $1 $2 $3 $4 $5 $6
#   tar -czf /home/vrogojin/biomedicum/FBL-paper-exec_$( date '+%Y_%m_%d' ).tar.gz $EXEC_DIR

cp log_netco4biomed/_global pipeline.log
#cat ../../result_page_template_header.html | sed "s/###/$SESSION_ID/g" | sed "s/<meta http-Equiv=\"Refresh\" Content=\"5\">//g" > result.html
sed -i 's/Refresh/---/g' result.html

if [ -s res ]
then
    status="PIPELINE TERMINATRED. STATUS OK"
else
    status="PIPELINE FAILED. CHECK THE LOG"
fi
sed -i "s/___STATUS___/$status/g" result.html

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontend "mkdir -p $SERVER_DIR/" &&
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -r result result.zip result.html pipeline.log frontend:$SERVER_DIR

#emailcommand="echo \"Results of the analysis for your query are ready for download. Please visit http://combio.abo.fi/web_services/remote_call/net_control/$SESSION_ID/result.html at your convenience\" | mail -s \"NetControl4BioMed: results $SESSION_ID\" $(cat useremail)"
#emailcommand="ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' frontent $emailcommand"
#eval '$emailcommand'

