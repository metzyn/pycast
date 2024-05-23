#!/bin/sh

id="4"

ip="10.1.2.40"
port="5000"

input="/tmp/cap.jpg"
output="/tmp/$id.jpg"
quality=1

while :
do
	screencapture -x $input
	sips -s format jpeg -s formatOptions $quality $input --out $output
	curl -X PUT -F "file=@$output" http://$ip:$port/upload

	sleep 5
done
