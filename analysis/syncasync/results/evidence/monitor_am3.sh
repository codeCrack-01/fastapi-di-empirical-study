#!/bin/bash
# Anomaly monitor for the amendment-3 knee run.
# Primary invariant: file handles on the SQLite DB must never exceed POOL=8.
# knee.py calls run_ramp once per rate, so a new uvicorn PID per rate step is
# EXPECTED; only same-arm repeated death would indicate a crash loop.
DB=/root/study/results/reviewgate_ro.db
OUT=/root/logs/monitor_am3.log
ANOM=/root/logs/monitor_am3_anomalies.log
: > $OUT; : > $ANOM
last_arm=""; arm_restarts=0; arm_max_db=0; arm_max_rss=0; arm_max_thr=0

while pgrep -f smoke_knees.py >/dev/null; do
  pid=$(ps -eo pid,args --no-headers | grep '[u]vicorn apps' | awk '{print $1}' | head -1)
  if [ -n "$pid" ]; then
    arm=$(tr '\0' ' ' < /proc/$pid/cmdline | sed 's/.*apps\.//;s/\.app.*//')
    dbh=$(readlink /proc/$pid/fd/* 2>/dev/null | grep -c "$DB")
    thr=$(awk '/Threads/{print $2}' /proc/$pid/status 2>/dev/null)
    rss=$(awk '/VmRSS/{print $2}' /proc/$pid/status 2>/dev/null)
    tot=$(ls /proc/$pid/fd 2>/dev/null | wc -l)
    echo "$(date +%H:%M:%S) arm=$arm pid=$pid db_fds=$dbh threads=$thr rss_kb=$rss total_fds=$tot" >> $OUT

    if [ "$arm" != "$last_arm" ]; then
      [ -n "$last_arm" ] && echo "ARM $last_arm complete: max_db_fds=$arm_max_db max_threads=$arm_max_thr max_rss_kb=$arm_max_rss starts=$arm_restarts" >> $OUT
      last_arm=$arm; arm_restarts=1; arm_max_db=0; arm_max_rss=0; arm_max_thr=0
    else
      arm_restarts=$((arm_restarts+1))
    fi
    [ "$dbh" -gt "$arm_max_db" ] && arm_max_db=$dbh
    [ "$thr" -gt "$arm_max_thr" ] && arm_max_thr=$thr
    [ "$rss" -gt "$arm_max_rss" ] && arm_max_rss=$rss

    [ "$dbh" -gt 10 ] && echo "ANOM $(date +%H:%M:%S) db_fds=$dbh exceeds POOL=8 on $arm" >> $ANOM
    
    if echo "$arm" | grep -q sync; then [ "$arm_max_thr" -gt 60 ] && echo "ANOM $(date +%H:%M:%S) sync threads=$arm_max_thr (anyio pool is 40)" >> $ANOM
    else [ "$arm_max_thr" -gt 20 ] && echo "ANOM $(date +%H:%M:%S) async threads=$arm_max_thr (main+8 aiosqlite expected ~10)" >> $ANOM; fi
    if [ "$arm_restarts" -gt 45 ]; then
      echo "ANOM $(date +%H:%M:%S) $arm started $arm_restarts times (crash loop? knee ladders are ~17-30 rate steps)" >> $ANOM
    fi
  else
    echo "$(date +%H:%M:%S) no-server (between rate steps)" >> $OUT
  fi
  sleep 20
done

{
  echo "=== RUN FINISHED $(date +%H:%M:%S) ==="
  echo "knee files written : $(ls /root/study/results/smoke_knees/*.json 2>/dev/null | wc -l) / 8"
  echo "db sha256          : $(sha256sum $DB | cut -d' ' -f1)"
  echo "db unchanged       : $([ "$(sha256sum $DB | cut -d' ' -f1)" = "ec432e8211b9767a114d9ff60f584e94038217bb3aa7a6590faecc38ed67fec8" ] && echo YES || echo NO)"
  echo "fd errors (run log): $(grep -c 'Too many open files' /root/logs/knees3.log)"
  echo "tracebacks (cells) : $(grep -l Traceback /root/study/results/cells/*.server.log 2>/dev/null | wc -l)"
  echo "fd errors (cells)  : $(grep -l 'Too many open files' /root/study/results/cells/*.server.log 2>/dev/null | wc -l)"
  echo "stray logs in /root/study: $(ls /root/study/*.log 2>/dev/null | wc -l)"
  echo "--- per-arm summary ---"; grep '^ARM' $OUT
  echo "--- ANOMALIES ---"; if [ -s $ANOM ]; then cat $ANOM; else echo "(none)"; fi
} >> $OUT 2>&1
