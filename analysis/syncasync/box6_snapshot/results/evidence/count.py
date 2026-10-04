import re, sys
p = "/root/study/results/cells/hx01.server.log"
txt = open(p, errors="replace").read()
blocks = txt.split("Thread 0x")
parked = [b for b in blocks if "core_read.py\", line 148" in b]
print("   thread dumps in dump      :", len(blocks))
print("   threads parked in sync_conn:", len(parked))
# anyio worker threads run via to_thread.run_sync -> WorkerThread
workers = [b for b in parked if "WorkerThread" in b or "run_sync" in b]
print("   ...of which anyio workers  :", len(workers))
print("   distinct thread ids        :",
      len({re.search(r"Thread 0x[0-9a-f]+", b).group(0) for b in parked if re.search(r"Thread 0x[0-9a-f]+", b)}))
# how many connections were still free
print("   frames mentioning get_db   :", txt.count("app.py\", line 30 in get_db"))
