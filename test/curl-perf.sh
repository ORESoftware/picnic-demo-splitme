#!/usr/bin/env bash


resume_path='/home/oleg/Desktop/Alexander_Mills.resume.2019.pdf'

sha="$(sha1sum "$resume_path" | awk '{print $1;}')"


for run in {1..1}; do

  for c in {1..1}; do

    sleep 1;
#

  ( curl -X POST -F "pdf=@$resume_path" "http://192.168.99.100:32449/split/$sha" ) &

#   ( curl "http://192.168.99.100:30838" ) &

  done;

done;

