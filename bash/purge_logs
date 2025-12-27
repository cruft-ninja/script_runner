#!/bin/sh
echo "yes mr, ninja sir, deleting old logs..."
sudo find /var/log -type f -name "*.old" -exec rm -f {} \;
sudo find /var/log -type f -name "*.gz" -exec rm -f {} \;
sudo find /var/log -type f -name "*.1" -exec rm -f {} \;
