import matplotlib.pyplot as plt
import numpy as np
import pickle
import algo
import HDD
import workload_gen

with open("./results/results.pickle", "rb") as f:
    R = pickle.load(f)
    for drive in HDD.DRIVES:
        num_algos = len(algo.ALGOS)
        num_workloads = len(workload_gen.WORKLOADS)

        # get energy plot
        fig, ax = plt.subplots()
        bar_width = 0.15
        index = np.arange(num_workloads)
        for i in range(num_algos):
            values = []
            for workload_name in workload_gen.WORKLOADS:
                stats = R[drive.name][workload_name]
                values.append(stats["Energy"][i])
            ax.bar(index + i * bar_width, values, bar_width, label=algo.ALGOS[i])
        ax.set_xlabel("Workloads")
        ax.set_ylabel("Consumption (Kilojoules)")
        ax.set_title("Total Energy Consumption " + drive.name)
        ax.set_xticks(index + bar_width * (num_algos - 1) / 2)
        ax.set_xticklabels(workload_gen.WORKLOADS)
        lgd = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        fig.savefig("./results/" + drive.name + "/" + "energy.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(fig)

        # get wait time plot
        fig, ax = plt.subplots()
        bar_width = 0.15
        index = np.arange(num_workloads)
        for i in range(num_algos):
            values = []
            for workload_name in workload_gen.WORKLOADS:
                stats = R[drive.name][workload_name]
                values.append(stats["Wait"][i])
            ax.bar(index + i * bar_width, values, bar_width, label=algo.ALGOS[i])
        ax.set_xlabel("Workloads")
        ax.set_ylabel("Seconds per request")
        ax.set_title("Average Wait Time Per Request " + drive.name)
        ax.set_xticks(index + bar_width * (num_algos - 1) / 2)
        ax.set_xticklabels(workload_gen.WORKLOADS)
        lgd = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        fig.savefig("./results/" + drive.name + "/" + "wait.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close(fig)




