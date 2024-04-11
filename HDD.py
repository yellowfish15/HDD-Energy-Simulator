class HDD:
  # storage is input in Gigabytes
  # power is input in Watts
  # time is input in Seconds
  def __init__(self,
               storage: float,
               sleeping_power: float, 
               standby_power: float,
               active_power: float,
               T_sd: float,
               T_wu: float,
               P_sd: float,
               P_wu: float):
    self.storage = storage
    # convert from joules per second to joules per millisecond
    self.sleeping_power = sleeping_power/1000
    self.standby_power = standby_power/1000
    self.active_power = active_power/1000
    self.P_sd = P_sd/1000
    self.P_wu = P_wu/1000
    # convert times from seconds to milliseconds
    self.T_sd = int(T_sd*1000)
    self.T_wu = int(T_wu*1000)


# the three HDDs we will simulate
A = HDD(6.4, 0.75, 3.48, 3.48, 0.51, 6.97, 2.12, 7.53)
B = HDD(500, 0.8, 9.3, 13, 10, 15, 9.3, 24)
C = HDD(2000, 0.25, 2.8, 3.7, 10, 8, 12, 30)
