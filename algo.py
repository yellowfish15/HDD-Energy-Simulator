import HDD
import random

# Default Algorithm
class Algorithm:
    def __init__(self, device: HDD):
        self.device = device
        self.backlog = 0 # number of requests backlogged
        self.state = 0 # 0 = active, 1 = standby, 2 = sleeping
        self.wu_tr = 0 # wake-up time remaining (2->0)
        self.sd_tr = 0 # shut-down time remaining (1->2)

    # call shutdown on an idle interval
    # assume that we are currently in standby state
    def shutdown(self, interval):
        energy = 0
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


# Timeout
class Timeout(Algorithm):
    # gamma is the threshold for the current idle period
    def __init__(self, device: HDD, gamma: int):
        self.gamma = gamma
        Algorithm.__init__(self, device)

    # override
    def run_algo(self, interval):
        if interval >= self.gamma:
            energy = self.gamma*self.device.standby_power
            interval -= self.gamma
            return energy + self.shutdown(interval)
        else:
            return interval*self.device.standby_power


# Exponential moving average
class EMA(Algorithm):
    # sigma is the number of idle periods to lookback
    def __init__(self, device: HDD, sigma: int):
        self.iterations = 0 # number of idle period iterations elapsed
        self.sigma = sigma
        self.smoothing = 2/(1+sigma)
        self.average = 0
        Algorithm.__init__(self, device)

    # override
    def run_algo(self, interval):
        self.iterations += 1
        if self.iterations < self.sigma:
            self.average += interval
            return interval*self.device.standby_power
        elif self.iterations == self.sigma:
            self.average += interval
            self.average /= self.sigma
            return interval*self.device.standby_power
        energy = 0
        if self.average >= self.device.alpha:
            energy = self.shutdown(interval)
        else:
            energy = interval*self.device.standby_power
            self.average *= 1-self.smoothing
            self.average += interval*self.smoothing
        return energy


class MarkovChain(Algorithm):
    def __init__(self, device, chain_len):
        self.chain_len = chain_len
        self.prs = {} # probabilities
        self.history = [] # history
        Algorithm.__init__(self, device)
    
    # override
    def run_algo(self, interval):
        energy = interval*self.device.standby_power
        flag = 1 if interval >= self.device.alpha else 0
        if len(self.history) == self.chain_len:
            hash = sum(j<<i for i,j in enumerate(reversed(self.history)))
            if hash in self.prs:
                p1 = 0 if 1 not in self.prs[hash] else self.prs[hash][1] # above threshold 
                p0 = 0 if 0 not in self.prs[hash] else self.prs[hash][0] # below threshold
                if p1+p0 > 0:
                    p = p1/(p1+p0)
                    if random.random() <= p: # we shutdown
                        energy = self.shutdown(interval)
                if flag not in self.prs[hash]:
                    self.prs[hash][flag] = 0
            else:
                self.prs[hash] = {}
                self.prs[hash][flag] = 0 
            self.prs[hash][flag] += 1
            self.history.pop(0)
        # append whether or not the current interval was good to shut down
        self.history.append(flag)
        return energy


# L-shaped
class L(Algorithm):
    # theta is the threshold for how short the previous busy period should be
    def __init__(self, device: HDD, theta: int):
        self.theta = theta
        self.prev = theta+1 # length of previous busy period
        Algorithm.__init__(self, device)

    # override
    def busy(self, interval):
        self.prev = interval
        return Algorithm.busy(self, interval)

    # override
    def run_algo(self, interval):
        if self.prev <= self.theta:
            return self.shutdown(interval)
        return interval*self.device.standby_power
