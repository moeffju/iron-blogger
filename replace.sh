#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Arguments: old-nick new-nick"
	exit 2
fi

old=$1
new=$2

sed -i "s/$old/$new/g" ledger bloggers.yml out/report.yml
grep -r $old .
