import pickle
import algo
import HDD

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
    print("Statistics:")
    print("Total Enery Consumption (Joules):", f"{total_consumption:.4f}")
    print("Average wait time per request (ms/request):", f"{total_wait_time/request_count:.4f}")


# de-serialize workload file
with open("wrkld", "rb") as f:
    W = pickle.load(f)

    print("--- Default Algorithm HDD A ---")
    run(algo.Algorithm(HDD.A), W)

    print("--- Timeout Algorithm HDD A ---")
    run(algo.Timeout(HDD.A, 1000), W)
    
    print("--- Markov Chain Algorithm HDD A ---")
    run(algo.MarkovChain(HDD.A, 2), W)
    
    print("--- EMA Algorithm HDD A ---")
    run(algo.EMA(HDD.A, 5), W)

    print("--- Logistic Regression Algorithm HDD A ---")
    run(algo.Logreg(HDD.A, W, 10), W)

    print("--- L-Shape Algorithm HDD A ---")
    run(algo.L(HDD.A, 10000), W)