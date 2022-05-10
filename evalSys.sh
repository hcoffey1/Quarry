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

log=tmp.log
n=10
for i in `find . -type f -wholename "${1}*.qasm"`; do
    [ -f "$i" ] || break
     /bin/time --verbose python ./src/Est.py $i simulation --n ${n} 2>> ${log} || exitScript ${i} 'simulation'
     /bin/time --verbose python ./src/Est.py $i p1 --n ${n} 2>> ${log} || exitScript ${i} 'p1'
     /bin/time --verbose python ./src/Est.py $i p2 --n ${n} 2>> ${log} || exitScript ${i} 'p2'
     /bin/time --verbose python ./src/Est.py $i esp --n ${n} 2>> ${log} || exitScript ${i} 'esp'
done

