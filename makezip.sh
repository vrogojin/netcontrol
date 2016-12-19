#!/bin/bash

mkdir result

cp @var1@ result/visual.pdf
cp @var2@ result/
cp @var3@ result/driven.csv
cp @var4@ result/extra.csv
cp @var5@ result/
cp @var6@ result/message.txt
cp @var6@ result/res

zip @optOut1@ -r result
