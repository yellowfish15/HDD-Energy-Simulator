import matplotlib.pyplot as plt
import pickle
import HDD
import workload_gen

# make a bar graph
def make_bar(algorithms: list, values: list, col: str, title: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(algorithms, values, color=col)
    ax.set_xlabel("Algorithm")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(range(len(algorithms)))
    ax.set_xticklabels(algorithms, rotation=45, ha="right")
    return fig


with open("./results/results.pickle", "rb") as f:
    R = pickle.load(f)
    for drive in HDD.DRIVES:
        for workload_name in workload_gen.WORKLOADS:
            stats = R[drive.name][workload_name]
            plot = make_bar(stats["Algorithm"], stats["Energy"], "b", "Total Energy Consumption", "Consumption (Kilojoules)")
            plot.savefig("./results/" + drive.name + "/" + workload_name + "-energy.pdf")
            plt.close(plot)
            plot = make_bar(stats["Algorithm"], stats["Wait"], "r", "Average Wait Time Per Request", "seconds per request")
            plot.savefig("./results/" + drive.name + "/" + workload_name + "-wait.pdf")
            plt.close(plot)
