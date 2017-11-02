#!/bin/bash

cat ../../result_page_template_header.html | sed "s/###/$SESSION_ID/g" > result.html
echo "<small>Backend version: " >> result.html
cat ../../version.txt >> result.html
echo "</small>" >> result.html
echo "<em>SESSION: $SESSION_ID<br/>" >> result.html
echo "Please wait!</br>" >> result.html
echo "<img src=\"https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif\" width=\"48px\" height=\"47px\"><br>" >> result.html
echo "Analyzing the network ...<br/>" >> result.html
echo "<br/>" >> result.html
echo "The pipeline is doing its best to deliver the results to you ASAP. This computation may take loooong time<br/></em>" >> result.html
echo "<h2>LOG:</h2><br/>" >> result.html
echo "<iframe src=\"pipeline.log.html#end\" id=\"frame\" width=\"90%\" height=\"400\">" >> result.html
echo "THE LOG CANNOT BE SHOWN" >> result.html
echo "</iframe><br/>" >> result.html
echo "<a href=\"session_control.php\" target=\"frame\">PIPELINE EMERGENCY STOP</a> (WARNING! Emergency stop cannot be reverted. All current progress will be lost!)<br/>" >> result.html
if [ -e "network.graphml" ]
then
    echo "<a href=\"network.graphml\" target=\"_new\">NETWORK.GRAPHML</a><br/>" >> result.html
fi
if [ -e "network.pdf" ]
then
    echo "<a href=\"network.pdf\" target=\"_new\">NETWORK.PDF</a><br/>" >> result.html
fi
if [ -e "network.txt" ]
then
    echo "<a href=\"network.txt\" target=\"_new\">NETWORK.TXT</a><br/>" >> result.html
fi
cat ../../result_page_template_footer.html >> result.html
