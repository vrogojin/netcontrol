#!/bin/bash

infile=@var1@

while read line
do
  temp="${line%\"}"
  temp="${temp#\"}"
  echo $temp >> @optOut1@
done < $infile