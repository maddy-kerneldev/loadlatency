# loadlatency
Script to understand system-wide and per-cpu load latency using PMU/thresholding feature

Scripts needs perf.data created using commandline
(preferably kernel 5.12+ or RHEL8.5 or SLES15 SP4)

	#sudo perf record --weight -e "{cpu/event=0x672C0101EC,thresh_cmp=10/}":u -a sleep 10

   Event:
    - Custom event (on top of PM_THRESH_MET-0x101ec) that programs Threshold logic for load only sampling,
      along with counting of cycles from issue to complete.
    - ":u" modifier is used to capture only userspace. 
    - "-a" option is used for system-wide sampling

Script Uages:

   /* Tunable for histogram interval, ex. 70 */
   /* default: 20 */

    #export SCRIPT_HISTOGRAM_INTERVAL=

   /* Tunable to look samples for specific TID, ex 10842 */
   /* default: All samples in the perf.data file */

    #export SCRIPT_HISTOGRAM_TTID=

    #sudo perf script -i <path to perf.data file> -s ./llatency-script.py

Sample data output from the llatency-script.py script 

Load Latency Histogram for TID 10842 total number of samples #      623
-------------------------------------------------------------------------------

|     Cycles  |    Counts |
|-------------|-----------|	
|   0 - 70    |  547      |
| 71 - 140    |   60      | 
|141 - 210    |   13      | 
|211 - 280    |    2      |
|281 - 350    |    0      |
|   > 421:    |    1      |

