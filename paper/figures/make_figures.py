import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "figure.dpi": 300,
    "font.family": "DejaVu Sans",
})

OUT = "/home/zain_khan/Documents/Fall'26/research_fastapi/paper/figures"

# --- Figure 1: construct prevalence (from rq1_constructs.csv) ---
constructs = ["C1 Depends", "C4 Generator/yield", "C3 Annotated[..., Depends]",
              "C2 Security", "Z  none (0 constructs)"]
repos = [303, 162, 104, 42, 98]
pcts = [75.4, 40.3, 25.9, 10.4, 24.4]
order = sorted(range(len(constructs)), key=lambda i: repos[i])
fig, ax = plt.subplots(figsize=(4.6, 2.3))
ypos = list(range(len(constructs)))[::-1]
bars = ax.barh(ypos, [repos[i] for i in order], color="#2b7bba", edgecolor="black", linewidth=0.4)
for bar, i in zip(bars, order):
    ax.text(bar.get_width() + 6, bar.get_y() + bar.get_height() / 2,
            f"{repos[i]} ({pcts[i]:.1f}%)", va="center", fontsize=8)
ax.set_yticks(ypos)
ax.set_yticklabels([constructs[i] for i in order], fontsize=8)
ax.set_xlabel("Repositories using the construct (of 402)")
ax.set_axisbelow(True)
ax.xaxis.grid(True, linestyle=":", alpha=0.5)
ax.set_xlim(0, 335)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_constructs.pdf")
plt.close(fig)

# --- Figure 2: hub fan-in (from analysis/out usage_patterns_summary.md) ---
hubs = ["get_db", "get_session", "get_current_user", "require_admin",
        "require_user", "get_db_session", "get_current_active_user", "require_role"]
fanin = [4683, 1732, 1471, 1175, 635, 537, 463, 454]
fig, ax = plt.subplots(figsize=(4.2, 2.7))
bars = ax.barh(list(range(len(hubs)))[::-1], fanin, color="#e15759", edgecolor="black", linewidth=0.4)
for bar, n in zip(bars, fanin):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2, f"{n:,}", va="center", fontsize=8)
ax.set_yticks(range(len(hubs)))
ax.set_yticklabels(hubs, fontsize=8.5)
ax.set_xlabel("Dependent functions (fan-in)")
ax.set_axisbelow(True)
ax.xaxis.grid(True, linestyle=":", alpha=0.5)
ax.set_xlim(0, 5100)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/fig_hubs.pdf")
plt.close(fig)

print("figures written")