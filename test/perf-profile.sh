#!/usr/bin/env bash

# curl http://192.168.99.100:31508
# http://192.168.99.100:30010

resume_path='/home/oleg/Desktop/Alexander_Mills.resume.2019.pdf'

sha="$(sha1sum "$resume_path" | awk '{print $1;}')"

ab -c 10 —n 500 "192.168.99.100:30010/split/$sha"