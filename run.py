import pandas as pd
import pickle
import algo
import HDD
import workload_gen

def run(A: algo.Algorithm, W: list):
    total_consumption = 0
    total_wait_time = 0
    request_count = 0
    for i in W:
        # ignore if interval == 0
        wait_time = 0
        if i < 0: # idle
            energy_consumption, wait_time = A.idle(-i)
        elif i > 0: # busy 
            energy_consumption, wait_time = A.busy(i)
            request_count += i
        total_consumption += energy_consumption
        total_wait_time += wait_time
    return total_consumption/1000, total_wait_time/(1000*request_count)


# test all algorithms on a workload
def test_workload(drive_name: str, hd: HDD, workload_name: str, ):
    try:
        # de-serialize workload file
        with open("./workloads/"+drive_name+"/"+workload_name, "rb") as f:
            W = pickle.load(f)
            stats = {
                "Energy": [], # Total Enery Consumption (Kilojoules)
                "Wait": [] # Average wait time per request (s/request)
            }

            # following ordering in algo.ALGOS
            e, w = run(algo.Algorithm(hd), W)
            stats["Energy"].append(e)
            stats["Wait"].append(w)

            e,w = run(algo.Timeout(hd, 0), W)
            stats["Energy"].append(e)
            stats["Wait"].append(w)
            
            e,w = run(algo.MarkovChain(hd, 4), W)
            stats["Energy"].append(e)
            stats["Wait"].append(w)
            
            e,w = run(algo.EMA(hd, 5), W)
            stats["Energy"].append(e)
            stats["Wait"].append(w)

            e,w = run(algo.Logreg(hd, W, 10), W)
            stats["Energy"].append(e)
            stats["Wait"].append(w)

            e,w = run(algo.L(hd, 11000), W)
            stats["Energy"].append(e)
            stats["Wait"].append(w)
            return pd.DataFrame(stats)
    except:
        return pd.DataFrame()


results = {} # dictionary of pandas dataframes [drive name] -> [workload name] -> data frame
for drive in HDD.DRIVES:
    results[drive.name] = {}
    for workload_name in workload_gen.WORKLOADS:
        results[drive.name][workload_name] = test_workload(drive.name, drive, workload_name+".pickle")

with open("./results/results.pickle", "wb") as f:
    pickle.dump(results, f)