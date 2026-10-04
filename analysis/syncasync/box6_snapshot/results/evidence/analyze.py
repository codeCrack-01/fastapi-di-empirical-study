import re, collections

PREFIX = "File "
txt = open("/root/study/results/cells/wedge.server.log", errors="replace").read()
blocks = txt.split("Thread 0x")
print("thread dumps: %d" % len(blocks))

waiting, holders = [], []
for b in blocks:
    if 'core_read.py", line 148' in b:
        waiting.append(b)
    elif b.strip():
        holders.append(b)

print("parked in queue.get (core_read.py:148): %d" % len(waiting))
print("other threads                      : %d" % len(holders))
print("")
print("=== NON-waiting threads ===")
for i, b in enumerate(holders):
    lines = b.splitlines()
    hdr = lines[0][:60] if lines else "?"
    frames = [l.strip() for l in lines if l.strip().startswith(PREFIX)]
    key = []
    for f in frames[-5:]:
        m = re.search(r'File "([^"]+)", line (\d+) in (\S+)', f)
        if m:
            key.append("%s:%s:%s" % (m.group(1).split("/")[-1], m.group(2), m.group(3)))
    print("  [%d] %s" % (i, hdr))
    print("      %s" % " <- ".join(key)[:300])

print("")
print("=== innermost frame per NON-waiting thread ===")
c = collections.Counter()
for b in holders:
    frames = [l.strip() for l in b.splitlines() if l.strip().startswith(PREFIX)]
    if frames:
        m = re.search(r'File "([^"]+)", line (\d+) in (\S+)', frames[0])
        if m:
            c["%s:%s:%s" % (m.group(1).split("/")[-1], m.group(2), m.group(3))] += 1
for k, v in c.most_common(12):
    print("  %3dx %s" % (v, k))
