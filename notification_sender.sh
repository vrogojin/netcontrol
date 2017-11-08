#!/bin/bash


curl -s --user api:key-94150297dc758aeb592079c4cd2307bd \
    https://api.mailgun.net/v3/mg.vrogojin.net/messages \
    -F from="$1" \
    -F to="$2" \
    -F subject="$3" \
    -F text="$4"