#!/bin/bash

# Remove all .aag, .cnf, .aig, and .tmp files from the current directory
rm -f *.aag *.cnf *.dnf *.aig *.tmp *.out tri.* vertices.txt vertices.ext  numOfLatticePoints cdd_output.txt numOfUnimodularCones totalTime latte_stats Check_emp.* matrix.ext latte.ext trace.log matrix out perf.data perf.data.old *.ine *.ext *.ext_temp *.samples

echo "All .aag, .cnf, .aig, and .tmp files have been removed from the current directory."