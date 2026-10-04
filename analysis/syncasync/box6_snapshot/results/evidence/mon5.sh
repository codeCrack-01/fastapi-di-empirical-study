#!/bin/bash
# Monitor for the amendment-5 smoke run.
# Watches for the exact failure classes seen so far:
#   1. a NULL cell (zero requests / achieved 0) - the fractional-rate bug
#   2. file-descriptor exhaustion - the async pool bug
#   3. handles on the SQLite file exceeding POOL=8 - the pool bound
#   4. runaway threads or RSS - a pool that leaks something other than fds
#   5. stray cell logs landing outside results/cells - the log-path bug
# Ends when the run log reports "done", or after a hard timeout.
DB=/root/study/results/reviewgate_ro.db
LOG=/root/logs/smoke5.log
OUT=/root/logs/mon5.log
ANOM=/root/logs/mon5_anomalies.log
CSV=/root/study/results/smoke/cells.csv
: > $OUT; : > $ANOM
seen=0
deadline=$(( $(date +%s) + 12000 ))

while :; do
  # run finished?
  if grep -q "^done  " $LOG 2>/dev/null; then
    echo "$(date +%H:%M:%S) run finished" >> $OUT; break
  fi
  if [ "$(date +%s)" -gt "$deadline" ]; then
    echo "$(date +%H:%M:%S) TIMEOUT guard hit" >> $ANOM; break
  fi

  # 1. null cells: any row with 0 requests, 0 achieved, or null p95
  n=$(($(wc -l < $CSV 2>/dev/null || echo 1) - 1))
  if [ "$n" -gt "$seen" ]; then
    for ((i=seen; i<n; i++)); do
      row=$(sed -n "$((i+2))p" $CSV)
      cond=$(echo "$row" | cut -d, -f1)
      reqs=$(echo "$row" | cut -d, -f16)
      ach=$(echo "$row" | cut -d, -f19)
      p95=$(echo "$row" | cut -d, -f13)
      if [ -z "$reqs" ] || [ "$reqs" = "0" ]; then
        echo "ANOM $(date +%H:%M:%S) NULL CELL $cond requests='$reqs' achieved='$ach'" >> $ANOM
      elif [ -z "$p95" ] || [ "$p95" = "" ]; then
        echo "ANOM $(date +%H:%M:%S) NULL p95 on $cond (requests=$reqs)" >> $ANOM
      fi
    done
    seen=$n
    echo "$(date +%H:%M:%S) cells=$n  last=$(tail -1 $CSV | cut -d, -f1)" >> $OUT
  fi

  # 3/4. live server resource state
  pid=$(ps -eo pid,args --no-headers | grep '[u]vicorn apps' | awk '{print $1}' | head -1)
  if [ -n "$pid" ]; then
    arm=$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null | sed 's/.*apps\.//;s/\.app.*//')
    dbh=$(readlink /proc/$pid/fd/* 2>/dev/null | grep -c "$DB")
    thr=$(awk '/Threads/{print $2}' /proc/$pid/status 2>/dev/null)
    rss=$(awk '/VmRSS/{print $2}' /proc/$pid/status 2>/dev/null)
    [ "$dbh" -gt 10 ] && echo "ANOM $(date +%H:%M:%S) db_fds=$dbh > POOL=8 on $arm" >> $ANOM
    case "$arm" in
      *sync) [ "$thr" -gt 60 ] && echo "ANOM $(date +%H:%M:%S) sync threads=$thr" >> $ANOM ;;
      *async) [ "$thr" -gt 20 ] && echo "ANOM $(date +%H:%M:%S) async threads=$thr (expect ~10)" >> $ANOM ;;
    esac
    echo "$(date +%H:%M:%S) $arm db_fds=$dbh threads=$thr rss_kb=$rss cells=$n" >> $OUT
  fi

  # 2. fd exhaustion / tracebacks in any cell log
  if grep -qs "Too many open files" /root/study/results/cells/*.server.log 2>/dev/null; then
    echo "ANOM $(date +%H:%M:%S) 'Too many open files' in a cell log" >> $ANOM
  fi
  # 5. stray logs outside results/cells
  stray=$(ls /root/study/*.log 2>/dev/null | wc -l)
  [ "$stray" -gt 0 ] && echo "ANOM $(date +%H:%M:%S) $stray stray log(s) in /root/study" >> $ANOM

  sleep 20
done

{
  echo "=== MONITOR END $(date +%H:%M:%S) ==="
  echo "cells in csv     : $(( $(wc -l < $CSV 2>/dev/null || echo 1) - 1 )) / 85"
  echo "null cells       : $(grep -c 'NULL CELL' $ANOM 2>/dev/null || echo 0)"
  echo "db unchanged     : $([ "$(sha256sum $DB|cut -d' ' -f1)" = "ec432e8211b9767a114d9ff60f584e94038217bb3aa7a6590faecc38ed67fec8" ] && echo YES || echo NO)"
  echo "fd errors (cells): $(grep -ls 'Too many open files' /root/study/results/cells/*.server.log 2>/dev/null | wc -l)"
  echo "tracebacks (cells): $(grep -ls Traceback /root/study/results/cells/*.server.log 2>/dev/null | wc -l)"
  echo "max db_fds       : $(grep -o 'db_fds=[0-9]*' $OUT | grep -o '[0-9]*$' | sort -n | tail -1)"
  echo "--- ANOMALIES ---"
  if [ -s $ANOM ]; then sort -u $ANOM; else echo "(none)"; fi
} >> $OUT 2>&1
