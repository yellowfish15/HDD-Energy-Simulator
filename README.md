
# HDD-Energy-Simulator
Simulate various power-down algorithms on several workload distributions using statistics collected from commercial Hard-Disk Drives.

Our [paper](./paper.pdf) containing motivation, methodology, and results of this study.

## Requirements
- Python 3.x
- pandas
- matplotlib
- numpy
  
## Installation
1. Clone the repository:
```git clone https://github.com/yellowfish15/HDD-Energy-Simulator.git```
2. Navigate to the directory.
3. Install dependencies:
```pip install -r requirements.txt```

## Usage
### ```workload_gen.py```
This python script allows you to generate workloads with different characteristics. You can customize the workload generation by modifying the parameters in the script. The script contains functions for generating workloads using various probability distributions and functions:

-   `gen_normal`: Generates workload intervals from normal distributions for both busy and idle periods.
-   `gen_exp`: Generates workload intervals from a normal distribution for busy periods and an exponential distribution for idle periods.
-   `gen_long_short`: Generates workload intervals from normal distributions for both busy and idle periods, with long and short intervals.
-   `gen_periodic`: Generates workload intervals from normal distributions for busy periods and a periodic function for idle periods.

You can adjust the parameters such as mean ($\mu$), standard deviation ($\sigma$), lambda ($\lambda$), amplitude ($a$), and wavelength constant ($k$) to customize the characteristics of the generated workloads.

After customizing the workload generation functions, you can serialize the generated workloads into files for later use. The script serializes the workloads for each of the three different HDDs (HDD A, HDD B, HDD C) into pickle files.

Run the Python script to generate and serialize the customized workloads: `python generate_workloads.py` 
The serialized workload files will be stored in the `workloads` directory.

### ```run.py```
This script runs the serialized workloads against the various algorithms described in ```algo.py```. The ```test_workload``` function loads the serialized workload file, runs different algorithms on it, and returns a pandas DataFrame containing the performance statistics. Feel free to adjust the algorithm input parameters in this function to compare results. 

Run the Python script to generate the results into a serialized file: `python run.py` 
The serialized results file will be in the `results` directory.

### ```get_results.py```
After running algorithms on the workloads and serializing the results, you can generate graphs to visualize the performance metrics such as total energy consumption and average wait time per request across different algorithms and workloads. This script allows you to automate the process of generating these graphs.

Run the Python script to generate the graphs with Mathplotlib: `python get_results.py` 
The generated graphs will be saved as PDF files in the `results` directory under each of the three tested HDDs.

## Additional Files
- ```algo.py``` contains the implementation of the five algorithms discussed in our study, plus the default "no" algorithm.
- ```HDD.py``` contains the implementation of the three sample HDDs we chose to simulate in our study.
- ```constants.py``` simply contain some miscellaneous constants used across the files to prevent re-running workload generations.

## Results
The visual results of our study used in our paper are contained in the `results` directory, sorted by the Hard Drive the result was collected on. Running ```get_results.py``` will re-generate these graphs on the workloads found in the `workloads` directory.