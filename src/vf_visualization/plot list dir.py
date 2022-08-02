from plot_IBIposture import plot_IBIposture
from plot_timeseries import (plot_raw, plot_aligned)
from plot_bout_timing import plot_bout_timing
from plot_kinetics import plot_kinetics
from plot_fin_body_coordination import plot_atk_ang_posture_chg
from plot_parameters import plot_parameters
import matplotlib.pyplot as plt

def main(root):
    plt.close('all')
    plot_bout_timing(root)
    
    plt.close('all')
    plot_IBIposture(root)
    
    plt.close('all')
    plot_parameters(root)
    
    plt.close('all')
    plot_kinetics(root)
    
    # Timeseries for aligned bouts may take long to plot for large dataset (>10GB)
    plt.close('all')
    plot_aligned(root)
    
    plt.close('all')
    plot_atk_ang_posture_chg(root) 
    
    plt.close('all')
    # plot_raw(root)
    
if __name__ == "__main__":
    list_dir = [
        # "/Volumes/LabData/manuscript data/2022-07 VF method/behavior data/partial_data_for_ana/DD_4dpf",
        "/Volumes/LabData/manuscript data/2022-07 VF method/behavior data/partial_data_for_ana/DD_7dpf",
        "/Volumes/LabData/manuscript data/2022-07 VF method/behavior data/partial_data_for_ana/DD_14dpf"]
    for root_dir in list_dir:
        main(root_dir)