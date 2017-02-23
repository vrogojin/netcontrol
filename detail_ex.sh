#!/bin/bash

cfile=@var1@
dfile=@var2@


grep "<-" $dfile > tmp.txt


while read line
do
  if grep -q "$line" tmp.txt; then
    grestr=($(grep "$line" tmp.txt))
    if [ "${filestr/${grestr[0]}}" = "$filestr" ]; then
	filestr="$filestr${grestr[0]}\n"
      else
	filestr=$filestr
    fi
  fi
  
done < $cfile
out="$filestr\n"
printf	$out > @optOut2@