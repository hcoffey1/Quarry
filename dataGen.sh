#!/bin/bash

for i in $(seq 1 $1); do
	python ./src/dataGen.py
done
