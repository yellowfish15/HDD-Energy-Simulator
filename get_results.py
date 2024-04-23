import matplotlib.pyplot as plt
import numpy as np
import pickle
from constants import ALGOS, WORKLOADS
import HDD

def make_plot(statskey: str, ylabel: str, title:str):
    fig, ax = plt.subplots()
    bar_width = 0.15
    index = np.arange(num_workloads)
    print(title)
    print("%20s" % (""), WORKLOADS)
    for i in range(num_algos):
        values = []
        for workload_name in WORKLOADS:
            stats = R[drive.name][workload_name]
            values.append(stats[statskey][i])
        ax.bar(index + i * bar_width, values, bar_width, label=ALGOS[i])
        print("%20s" % (ALGOS[i]), values)
    print()
    ax.set_xlabel("Workload Distribution")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(index + bar_width * (num_algos - 1) / 2)
    ax.set_xticklabels(WORKLOADS)
    lgd = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    return fig, lgd


with open("./results/results.pickle", "rb") as f:
    R = pickle.load(f)
    for drive in HDD.DRIVES:
        num_algos = len(ALGOS)
        num_workloads = len(WORKLOADS)

        # get energy plot
        fig, lgd = make_plot("Energy", "Energy Consumption (Watt-hours)", "Total Energy Consumption " + drive.name)
        fig.savefig("./results/" + drive.name + "/" + "energy.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(fig)

        # get wait time plot
        fig, lgd = make_plot("Wait", "Milliseconds per request", "Average Wait Time Per Request " + drive.name)
        fig.savefig("./results/" + drive.name + "/" + "wait.pdf", bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(fig)
