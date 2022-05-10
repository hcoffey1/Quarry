#!/bin/bash
#Hayden Coffey
#Used to collect system performance metrics for different query modes

function exitScript {
    echo "Run failed!"
    echo "File: ${1}"
    echo "Mode: ${2}"
    exit
}

if [ "$#" != 1 ]; then
    echo "Need to specify path to dir with qasm files."
    exit
fi

log=$(date +"%Y-%m-%d_%H-%M-%S").log
n=10
for i in `find . -type f -wholename "${1}*.qasm"`; do
    [ -f "$i" ] || break
    /bin/time --verbose python ./src/Est.py $i swap_compile --n ${n} 2>> ${log} || exitScript ${i} 'swap_compile'
    /bin/time --verbose python ./src/Est.py $i swap_pred --n ${n} 2>> ${log} || exitScript ${i} 'swap_pred'
done