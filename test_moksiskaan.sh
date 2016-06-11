## This script invokes data importing pipeline for FBL paper
## "Identifying central genes in gene networks by counting feedback loops"
## Invoking file get_data_for_ieee_paper.and

#!/bin/bash

export MOKSISKAAN_HOME=/opt/moksiskaan/db
#export EXEC_DIR=/home/vrogojin/biomedicum/FBL-paper-exec
#export VR_PIPELINES_HOME=/home/vrogojin/mercurial-reps/vrogojin/FBL-studies
#export BETA_BUNDLE=/home/vrogojin/anduril-svn/trunk/beta
source $MOKSISKAAN_HOME/pipeline/execInit.sh

../../final_pipeline.and

#   anduril run -d $EXEC_DIR -b $MOKSISKAAN_HOME/pipeline -b $ANDURIL_HOME/sequencing -b $ANDURIL_HOME/beta -threads 8 $VR_PIPELINES_HOME/get_data_for_ieee_paper.and $1 $2 $3 $4 $5 $6
#   tar -czf /home/vrogojin/biomedicum/FBL-paper-exec_$( date '+%Y_%m_%d' ).tar.gz $EXEC_DIR