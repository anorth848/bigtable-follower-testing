#!/usr/bin/env bash

export BIGTABLE_EMULATOR_HOST=127.0.0.1:8086

user=$(echo $1 | md5sum | sed -e 's/ .*//')

rownum=20000

while :
do 
  rowkey=$user:following:$(echo $rownum | md5sum | sed -e 's/ .*//' )
  cbt -project no-project -instance emulator \
  set test $rowkey something:foo=online something:online=
  echo "added $rowkey"
  (( rownum = $rownum + 1 ))
done


