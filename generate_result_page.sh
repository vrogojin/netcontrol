#!/bin/bash

cat ../../result_page_template_header.html | sed "s/###/$SESSION_ID/g" > result.html
echo "<a href=\"../remote_call.php\">&lt;&lt;BACK TO PIPELINE DASHBOARD</a>" >> result.html
echo "<hr/>" >> result.html
echo "<small>Backend version: " >> result.html
cat ../../version.txt >> result.html
echo "</small><br/>" >> result.html
echo "<em>SESSION: $SESSION_ID</em><br/><br/>" >> result.html
cat status.txt >> result.html
if grep -q 'STOP' control.txt; then
    echo "<br/>PIPELINE HALTED!"
else
    if grep -q 'Log closed' log_netcon4biomed/_global;  then
	echo PIPELINE TERMINATED. OK
    else
	echo "<a href=\"session_control.php\"> (!!!PIPELINE EMERGENCY STOP!!!)</a> <br/>(WARNING! Emergency stop cannot be reverted. All current progress will be lost!)<br/>" >> result.html
    fi
fi
state1=0
state2=0
state3=0
state4=0
state5=0

if grep -q "exec-1-" progress.txt; then
    state1=1
fi
if grep -q "done-1-" progress.txt; then
    state1=2
fi
if grep -q "skip-1-" progress.txt; then
    state1=3
fi
if grep -q "fail-1-" progress.txt; then
    state1=4
fi
if grep -q "exec-2-" progress.txt; then
    state2=1
fi
if grep -q "done-2-" progress.txt; then
    state2=2
fi
if grep -q "skip-2-" progress.txt; then
    state2=3
fi
if grep -q "fail-2-" progress.txt; then
    state2=4
fi
if grep -q "exec-3-" progress.txt; then
    state3=1
fi
if grep -q "done-3-" progress.txt; then
    state3=2
fi
if grep -q "skip-3-" progress.txt; then
    state3=3
fi
if grep -q "fail-3-" progress.txt; then
    state3=4
fi
if grep -q "exec-4-" progress.txt; then
    state4=1
fi
if grep -q "done-4-" progress.txt; then
    state4=2
fi
if grep -q "skip-4-" progress.txt; then
    state4=3
fi
if grep -q "fail-4-" progress.txt; then
    state4=4
fi
if grep -q "exec-5-" progress.txt; then
    state5=1
fi
if grep -q "done-5-" progress.txt; then
    state5=2
fi
if grep -q "skip-5-" progress.txt; then
    state5=3
fi
if grep -q "fail-5-" progress.txt; then
    state5=4
fi

echo "<hr/><pre>" >> result.html
if [ $state1 -eq 0 ]; then
    echo "<font color=gray>   INITIALIZATION...............................PENDING</font>" >> result.html
fi
if [ $state1 -eq 1 ]; then
    echo "<font color=orange> INITIALIZATION...............................RUNNING</font><img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"10px\" height=\"10px\">" >> result.html
fi
if [ $state1 -eq 2 ]; then
    echo "<font color=green>  INITIALIZATION...............................DONE</font>" >> result.html
fi
if [ $state1 -eq 3 ]; then
    echo "<font color=blue>   INITIALIZATION...............................SKIPPED</font>" >> result.html
fi
if [ $state1 -eq 4 ]; then
    echo "<font color=red>    INITIALIZATION...............................FAILED</font>" >> result.html
fi

if [ $state2 -eq 0 ]; then
    echo "<font color=gray>   NETWORK GENERATION...........................PENDING</font>" >> result.html
fi
if [ $state2 -eq 1 ]; then
    echo "<font color=orange> NETWORK GENERATION...........................RUNNING</font><img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"10px\" height=\"10px\">" >> result.html
fi
if [ $state2 -eq 2 ]; then
    echo "<font color=green>  NETWORK GENERATION...........................DONE</font>" >> result.html
fi
if [ $state2 -eq 3 ]; then
    echo "<font color=blue>   NETWORK GENERATION...........................SKIPPED</font>" >> result.html
fi
if [ $state2 -eq 4 ]; then
    echo "<font color=red>    NETWORK GENERATION...........................FAILED</font>" >> result.html
fi

if [ $state3 -eq 0 ]; then
    echo "<font color=gray>   PREPROCESSING................................PENDING</font>" >> result.html
fi
if [ $state3 -eq 1 ]; then
    echo "<font color=orange> PREPROCESSING................................RUNNING</font><img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"10px\" height=\"10px\">" >> result.html
fi
if [ $state3 -eq 2 ]; then
    echo "<font color=green>  PREPROCESSING................................DONE</font>" >> result.html
fi
if [ $state3 -eq 3 ]; then
    echo "<font color=blue>   PREPROCESSING................................SKIPPED</font>" >> result.html
fi
if [ $state3 -eq 4 ]; then
    echo "<font color=red>    PREPROCESSING................................FAILED</font>" >> result.html
fi

if [ $state4 -eq 0 ]; then
    echo "<font color=gray>   ANALYSIS: SEARCHING FOR INPUT NODES..........PENDING</font>" >> result.html
fi
if [ $state4 -eq 1 ]; then
    echo "<font color=orange> ANALYSIS: SEARCHING FOR INPUT NODES..........RUNNING</font><img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"10px\" height=\"10px\">" >> result.html
fi
if [ $state4 -eq 2 ]; then
    echo "<font color=green> ANALYSIS: SEARCHING FOR INPUT NODES...........DONE</font>" >> result.html
fi
if [ $state4 -eq 3 ]; then
    echo "<font color=blue>  ANALYSIS: SEARCHING FOR INPUT NODES...........SKIPPED</font>" >> result.html
fi
if [ $state4 -eq 4 ]; then
    echo "<font color=red>   ANALYSIS: SEARCHING FOR INPUT NODES...........FAILED</font>" >> result.html
fi

if [ $state5 -eq 0 ]; then
    echo "<font color=gray>  PREPARING THE OUTPUT..........................PENDING</font>" >> result.html
fi
if [ $state5 -eq 1 ]; then
    echo "<font color=orange>PREPARING THE OUTPUT..........................RUNNING</font><img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"10px\" height=\"10px\">" >> result.html
fi
if [ $state5 -eq 2 ]; then
    echo "<font color=green> PREPARING THE OUTPUT..........................DONE</font>" >> result.html
fi
if [ $state5 -eq 3 ]; then
    echo "<font color=blue>  PREPARING THE OUTPUT..........................SKIPPED</font>" >> result.html
fi
if [ $state5 -eq 4 ]; then
    echo "<font color=red>   PREPARING THE OUTPUT..........................FAILED</font>" >> result.html
fi
echo "</pre><hr/>" >> result.html
echo "<h3>DOWNLOAD</h3><br/>" >> result.html
if [ -e "network.graphml" ]
then
    echo "<a href=\"result/network.graphml\" target=\"_new\">NETWORK IN GRAPHML FORMAT DOWNLOAD</a><br/>" >> result.html
fi
if [ -e "network.pdf" ]
then
    echo "<a href=\"result/network.pdf\" target=\"_new\">NETWORK AS IMAGE</a><br/>" >> result.html
fi
if [ -e "network.txt" ]
then
    echo "<a href=\"result/network.txt\" target=\"_new\">NETWORK AS LIST OF EDGES</a><br/>" >> result.html
fi
if [ -e "result/driven.csv" ]
then
    echo "<a href=\"result/driven.csv\" target=\"_new\">ANALYSIS RESULT: LIST OF INPUT NODES TARGETED BY DRUGS</a><br/>" >> result.html
fi
if [ -e "result/extra.csv" ]
then
    echo "<a href=\"result/extra.csv\" target=\"_new\">ANALYSIS RESULT: LIST OF INPUT NODES (NOT KNOWN TO BE TARGETED BY DRUGS)</a><br/>" >> result.html
fi
if [ -e "result/details.txt" ]
then
    echo "<a href=\"result/details.txt\" target=\"_new\">ANALYSIS RESULT: REPORT</a><br/>" >> result.html
fi
if [ -e "result.zip" ]
then
    echo "<a href=\"result.zip\" target=\"_new\">ANALYSIS RESULT: ZIP ARCHIVE</a><br/>" >> result.html
fi
echo "<details>" >> result.html
echo "<summary>PIPELINE TECHNICAL LOG (click to view full)<br/>" >> result.html
echo "<hr/><code><pre>" >> result.html
tail pipeline.log >> result.html
echo "</pre></code><hr/>" >> result.html
echo "</summary><br/>" >> result.html
#echo "<iframe src=\"pipeline.log.html#end\" id=\"frame\" width=\"90%\" height=\"400\" scrolling=\"yes\">" >> result.html
#echo "THE LOG CANNOT BE SHOWN" >> result.html
#echo "</iframe><br/>" >> result.html
echo "<hr/><code><pre>" >> result.html
cat pipeline.log >> result.html
echo "</pre></code><hr/>" >> result.html

echo "</details>" >> result.html

cat ../../result_page_template_footer.html >> result.html
