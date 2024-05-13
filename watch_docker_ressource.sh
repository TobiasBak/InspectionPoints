#!/usr/bin/env zsh
while :
do
  tempstat=$(docker stats bachelorproject-proxy-1 --format='{{.Name}} {{.MemUsage}}  {{.CPUPerc}}' --no-stream)
  temptime=$(date +%H:%M:%S)
  temptime2=$(date +%s)
  echo $tempstat $temptime $temptime2 >> testing.csv
  sleep 1
done
