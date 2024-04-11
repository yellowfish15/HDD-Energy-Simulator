import pickle
import HDD

class Algorithm:
    def __init__(self, device: HDD):
        self.device = device
        self.backlog = 0 # number of requests backlogged
        self.state = 0 # 0 = active, 1 = standby, 2 = sleeping
        self.wu_tr = 0 # wake-up time remaining (2->0)
        self.sd_tr = 0 # shut-down time remaining (1->2)

    # pass in an idle interval
    def clear_backlog(self, interval):
        energy = 0 # energy consumption in joules
        wait = 0 # cumulative wait time across all requests
        if self.backlog == 0 or interval == 0:
            return energy, wait, interval
        if self.wu_tr == 0 and self.sd_tr == 0:
            if self.state == 2: # in shutdown state, so wake up
                self.wu_tr = self.device.T_wu
            elif self.state == 1: # switch to active state
                self.state = 0
        if self.wu_tr >= interval:
            energy = self.wu_tr * self.device.P_wu
            wait = self.backlog*interval
            self.wu_tr -= interval
            interval = 0
        elif self.wu_tr > 0 and self.wu_tr < interval: 
            energy = self.wu_tr*self.device.P_wu
            wait = self.backlog*self.wu_tr
            interval -= self.wu_tr
            self.wu_tr = 0 # reset the wake up timer
            self.backlog = 0 # reset the number of backlogged requests
            self.state = 0 # awake state
        elif self.sd_tr >= interval:
            energy = self.sd_tr * self.device.P_sd
            wait = self.backlog*interval
            self.sd_tr -= interval
            self.backlog += interval
            interval = 0
        elif self.sd_tr > 0 and self.sd_tr < interval:
            energy = self.sd_tr*self.device.P_sd
            wait = self.backlog*self.sd_tr
            interval -= self.sd_tr
            self.sd_tr = 0 # reset the shut down timer
            self.state = 2 # sleeping state
        elif self.state == 0: # take 1 millisecond to clear all requests
            energy = self.device.active_power
            wait = self.backlog
            interval -= 1
            self.backlog = 0
        if self.backlog > 0 and interval > 0:
            act_energy, act_wait, interval = self.clear_backlog(interval)
            energy += act_energy
            wait += act_wait
        return energy, wait, interval
        
    def idle(self, interval):
        energy, wait, interval = self.clear_backlog(interval) # clear any waiting requests
        if interval > 0: # backlog should be cleared
            # turn to standby power
            self.state = 1
            idle_energy = self.run_algo(interval)
            energy += idle_energy
        return energy, wait

    def busy(self, interval):
        if interval == 0:
            return 0, 0
        energy = 0 # energy consumption in joules
        wait = 0 # cumulative wait time across all requests
        if self.wu_tr == 0 and self.sd_tr == 0:
            if self.state == 2: # activate shutdown if in sleeping state
                self.wu_tr = self.device.T_wu
            elif self.state == 1: # switch to active state
                self.state = 0
        if self.wu_tr >= interval:
            energy = self.wu_tr * self.device.P_wu
            wait = interval*(interval+1)/2 + self.backlog*interval
            self.wu_tr -= interval
            self.backlog += interval
            interval = 0
        elif self.wu_tr > 0 and self.wu_tr < interval: 
            energy = self.wu_tr*self.device.P_wu
            wait = self.wu_tr*(self.wu_tr)/2 + self.backlog*self.wu_tr
            interval -= self.wu_tr
            self.wu_tr = 0 # reset the wake up timer
            self.backlog = 0 # reset the number of backlogged requests
            self.state = 0 # awake state
        elif self.sd_tr >= interval:
            energy = self.sd_tr * self.device.P_sd
            wait = interval*(interval+1)/2 + self.backlog*interval
            self.sd_tr -= interval
            self.backlog += interval
            interval = 0
        elif self.sd_tr > 0 and self.sd_tr < interval:
            energy = self.sd_tr*self.device.P_sd
            wait = self.sd_tr*(self.sd_tr)/2 + self.backlog*self.sd_tr
            interval -= self.sd_tr
            self.sd_tr = 0 # reset the shut down timer
            self.state = 2 # sleeping state
        elif self.state == 0: # active
            energy = interval*self.device.active_power
            wait = self.backlog
            interval = 0
            self.backlog = 0
        if interval > 0:
            act_energy, act_wait = self.busy(interval)
            energy += act_energy
            wait += act_wait
        return energy, wait
    
    # abstract method to be implemented by the algorithms
    def run_algo(self, interval):
        # default behavior (no algorithm)
        return interval*self.device.standby_power


class Timeout(Algorithm):
    def __init__(self, device: HDD, gamma: int):
        self.gamma = gamma
        Algorithm.__init__(self, device)

    # override
    def run_algo(self, interval):
        if interval >= self.gamma:
            energy = self.gamma*self.device.standby_power
            interval -= self.gamma
            # initiate shutdown
            self.sd_tr = self.device.T_sd
            if self.sd_tr >= interval: # T_sd covers entire interval
                energy += interval*self.device.P_sd
                self.sd_tr -= interval
                interval = 0
            else:
                energy += self.sd_tr*self.device.P_sd
                interval -= self.sd_tr
                self.sd_tr = 0
                self.state = 2
                energy += interval*self.device.sleeping_power
                interval = 0
            return energy
        else:
            return interval*self.device.standby_power


def run(A: Algorithm, W: list):
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

    print("--- Default Algorithm ---")
    A_default = Algorithm(HDD.A)
    run(A_default, W)

    print("--- Timeout Algorithm ---")
    A_timeout = Timeout(HDD.A, 1000)
    run(A_timeout, W)