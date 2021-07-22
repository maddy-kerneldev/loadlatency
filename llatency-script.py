#
# Script to understand system-wide and per-cpu load latency using PMU/thresholding feature 
#
# Madhavan Srinivasan, IBM Corp 2021
#
# Scripts needs perf.data created using commandline
# (preferably kernel 5.12+ or RHEL8.5 or SLES15 SP4)
#
#   #sudo perf record --weight -e "{cpu/event=0x672C0101EC,thresh_cmp=10/}":u -a sleep 10
#
# Event:
# - Custom event (on top of PM_THRESH_MET-0x101ec) that programs Threshold logic for load only sampling,
# along with counting of cycles from issue to complete.
# - ":u" modifier is used to capture only userspace. 
# - "-a" option is used for system-wide sampling
#
# Script Uages:
#
#   /* Tunable for histogram interval, ex. 70 */
#   /* Histogram: 0-70, 71-140 ..  */
#   /* default: 70 */
#   #export SCRIPT_HISTOGRAM_INTERVAL=
#
#   /* Tunable to look samples for specific TID, ex 10842 */
#   /* default: All samples in the perf.data file */
#   #export SCRIPT_HISTOGRAM_TTID=
#
#   #sudo perf script -i <path to perf.data file> -s ./llatency-script.py
#

from __future__ import print_function

import os
import sys

sys.path.append(os.environ['PERF_EXEC_PATH'] + \
    '/scripts/python/Perf-Trace-Util/lib/Perf/Trace')

from perf_trace_context import *
from Core import *

tsample=0
interval=0
hgram = {}
cpu_hgram = {}
range_dict = {}
range_dict_str = {}
ttid=0

def get_interval_val():
    global interval
    try:
        strg = os.environ['SCRIPT_HISTOGRAM_INTERVAL']
        interval = int(strg)
    except:
        interval = 70

def get_tid_track():
    global ttid
    try:
        strg = os.environ['SCRIPT_HISTOGRAM_TTID']
        ttid = int(strg)
    except:
        print("Export pid to track with SCRIPT_HISTOGRAM_TTID")
        ttid = -1

def init_dict():
    get_interval_val() 
    get_tid_track()
    start = 0
    dl=interval
    for i in range(5):
       kstr = ("%d - %d" % (start, dl))
       range_dict_str[i] = kstr
       hgram[kstr] = 0
       range_dict[i] = dl
       start = dl + 1
       dl += interval
    kstr = ("  > %d" %(dl+1)) 
    range_dict_str[5] = kstr
    hgram[kstr] = 0

def trace_begin():
    init_dict()

def trace_end():
     global tsample
     global ttid
     if (ttid > 0):
         print("Load Latency Histogram for TID %d total number of samples #%9d"%(ttid,tsample))
     else:    
         print("Load Latency Histogram - total number of samples #%9d"%(tsample))

     print("-------------------------------------------------------------------------")
     print()
     print("     Cycles      Counts ")
     print("%9s  %7d"%(range_dict_str[0],hgram[range_dict_str[0]]))
     print("%9s  %7d"%(range_dict_str[1],hgram[range_dict_str[1]]))
     print("%9s  %7d"%(range_dict_str[2],hgram[range_dict_str[2]]))
     print("%9s  %7d"%(range_dict_str[3],hgram[range_dict_str[3]]))
     print("%9s  %7d"%(range_dict_str[4],hgram[range_dict_str[4]]))
     print(" %5s:  %7d"%(range_dict_str[5],hgram[range_dict_str[5]]))

     print()

def calculate_wgt_glb(weight):
    global interval
    if (int(weight) <= int(interval)):
        hgram[range_dict_str[0]] += 1
    elif ((int(weight) >= (interval+1)) and (int(weight) <= (interval*2))):
        hgram[range_dict_str[1]] += 1
    elif ((int(weight) >= ((interval*2) + 1)) and (int(weight) <= (interval*3))):
        hgram[range_dict_str[2]] += 1
    elif ((int(weight) >= ((interval*3) + 1)) and (int(weight) <= (interval*4))):
        hgram[range_dict_str[3]] += 1
    elif ((int(weight) >= ((interval*4) + 1)) and (int(weight) <= (interval*5))):
        hgram[range_dict_str[4]] += 1
    elif (int(weight) >= ((interval*5) + 1)):
        hgram[range_dict_str[5]] += 1


def process_event(perf_sample_dict):
    global tsample
    global ttid
    cpu = perf_sample_dict['sample'].get('cpu')
    weight = perf_sample_dict['sample'].get('weight')
    tid = perf_sample_dict['sample'].get('tid')

    #For System Wide histogram update
    if(ttid <= 0):
        tsample += 1
        calculate_wgt_glb(int(weight))
    else:      
        if(ttid == int(tid)):
            tsample += 1
            calculate_wgt_glb(int(weight))
