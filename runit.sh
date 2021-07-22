#!/bin/bash
PCPU=1
rm -f runlog.log
for (( CCPU=0; CCPU<10; CCPU+=3 )); do
    echo $CCPU
    ./perf record --weight -e "{cpu/event=0x672C0101EC,thresh_cmp=10/}":u ./producer_consumer -p $PCPU -c $CCPU > log.log1
    TID=`cat log.log1 | grep ")\[P" | cut -d ' ' -f 2 | cut -d ']' -f 1`
    NS=`cat log.log1 | grep "access:" | cut -d '(' -f 3 | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
    #CYC=$(((NS * 4) + 5))
    echo "---------------- New Run ----------------------" >> runlog.log
    echo "producer_consumer -p $PCPU -c $CCPU Access time: $NS ns" >> runlog.log 
    export SCRIPT_HISTOGRAM_TTID=$TID
    PERF_EXEC_PATH=/home/maddy/linux/tools/perf/ ./perf script -s ./llatency-script.py  >> runlog.log
    rm -f log.log1
    echo "Done CCPU = $CCPU"	
done
