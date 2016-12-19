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

../../pipeline_kegg.and

#   anduril run -d $EXEC_DIR -b $MOKSISKAAN_HOME/pipeline -b $ANDURIL_HOME/sequencing -b $ANDURIL_HOME/beta -threads 8 $VR_PIPELINES_HOME/get_data_for_ieee_paper.and $1 $2 $3 $4 $5 $6
#   tar -czf /home/vrogojin/biomedicum/FBL-paper-exec_$( date '+%Y_%m_%d' ).tar.gz $EXEC_DIR

cp log_pipeline_kegg/_global pipeline.log
cat ../../result_page_template_header2.html > result.html
echo "<pre>" >> result.html
if [ -s res ]
then
    cat res >> result.html
else
    echo "<em><font color=red>THE PIPELINE EXECUTION FAILED!!!</font></em><samp>" >> result.html
    cat pipeline.log >> result.html
    echo "</samp>" >> result.html
fi
echo "</pre>" >> result.html
echo "SESSION: $SESSION_ID<br/>"
echo "<ul>" >> result.html
echo "<li><a href='result/network.pdf'>Network layout</a></li>" >> result.html
echo "<li><a href='result/network.graphml'>Network XML</a></li>" >> result.html
echo "<li><a href='result/driven.csv'>List of driven nodes serving as drug targets</a></li>" >> result.html
echo "<li><a href='result/extra.csv'>All other driven nodes</a></li>" >> result.html
echo "<li><a href='result/details.txt'>Detailed report on structuran network controllability analysis</a></li>" >> result.html
echo "<li><a href='result.zip'>ZIP archive</a></li>" >> result.html
echo "<hr>" >> result.html
echo "<li><a href='pipeline.log'>Pipeline LOG</a></li>" >> result.html
echo "</ul>" >> result.html
cat ../../result_page_template_footer.html >> result.html

ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' webadmin@combio.abo.fi "mkdir -p $SERVER_DIR/" &&
scp -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' -r result result.zip result.html pipeline.log webadmin@combio.abo.fi:$SERVER_DIR

emailcommand="'echo \"Results of the analysis for your query are ready for download. Please visit http://combio.abo.fi/web_services/remote_call/net_control/$SESSION_ID/result.html at your convenience\" | mail -s \"NetControl4BioMed: results $SESSION_ID\" $(cat useremail)'"
emailcommand="ssh -i ~/.ssh/id_rsa -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile /dev/null' webadmin@combio.abo.fi $emailcommand"
eval "$emailcommand"

