'''
plot correlation of features by time
1. corr of angular vel at each timpoint with preBoutPitch / atkAngle / trajectory deviation
2. corr of ins. trajectory at each timepoint with bout trajectory
trajectory deviation (trajecgtory residual) is defined as (bout_traj_peakecgtory - pitch_pre_bout)

'''

#%%
# import sys
import os,glob
import pandas as pd # pandas library
import numpy as np # numpy
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from plot_functions.get_data_dir import (get_data_dir, get_figure_dir)
from plot_functions.get_index import get_index
from plot_functions.plt_tools import (set_font_type, defaultPlotting, distribution_binned_average, distribution_binned_average_nostd, day_night_split)
from tqdm import tqdm
import matplotlib as mpl
set_font_type()

# %%
# Paste root directory here
# if_plot_by_speed = True
pick_data = 'all_7dd'
root, FRAME_RATE= get_data_dir(pick_data)

folder_name = f'{pick_data} corr plot_newTrajDeviation'
folder_dir6 = get_figure_dir('Fig_6')
folder_dir4 = get_figure_dir('Fig_4')

fig_dir4 = os.path.join(folder_dir4, folder_name)
fig_dir6 = os.path.join(folder_dir6, folder_name)

try:
    os.makedirs(fig_dir4)
except:
    pass
try:
    os.makedirs(fig_dir6)
except:
    pass   
peak_idx , total_aligned = get_index(FRAME_RATE)
idxRANGE = [peak_idx-int(0.27*FRAME_RATE),peak_idx+int(0.22*FRAME_RATE)]
spd_bins = np.arange(5,25,4)

# %% features for plotting
all_features = [
    'propBoutAligned_speed', 
    'propBoutAligned_accel',    # angular accel calculated using raw angular vel
    'linear_accel', 
    'propBoutAligned_pitch', 
    'propBoutAligned_angVel',   # smoothed angular velocity
    'propBoutInflAligned_accel',
    'propBoutAligned_instHeading', 
    'heading_sub_pitch',
            # 'propBoutAligned_x',
            # 'propBoutAligned_y', 
            # 'propBoutInflAligned_angVel',
            # 'propBoutInflAligned_speed', 
            # 'propBoutAligned_angVel_hDn',
            # # 'propBoutAligned_speed_hDn', 
            # 'propBoutAligned_pitch_hDn',
            # # 'propBoutAligned_angVel_flat', 
            # # 'propBoutAligned_speed_flat',
            # # 'propBoutAligned_pitch_flat', 
            # 'propBoutAligned_angVel_hUp',
            # 'propBoutAligned_speed_hUp', 
            # 'propBoutAligned_pitch_hUp', 
    'ang_speed',
    'ang_accel_of_SMangVel',    # angular accel calculated using smoothed angVel
    # 'xvel', 'yvel',

]

# %%
# CONSTANTS
# %%
T_INITIAL = -0.25 #s
T_PREP_200 = -0.2
T_PREP_150 = -0.15
T_PRE_BOUT = -0.10 #s
T_POST_BOUT = 0.1 #s
T_END = 0.2
T_MID_ACCEL = -0.05
T_MID_DECEL = 0.05
time_of_max_angSpd = -9.058456046407839/1000
separation_posture = 10
idx_initial = int(peak_idx + T_INITIAL * FRAME_RATE)
idx_pre_bout = int(peak_idx + T_PRE_BOUT * FRAME_RATE)
idx_post_bout = int(peak_idx + T_POST_BOUT * FRAME_RATE)
# idx_mid_accel = int(peak_idx + T_MID_ACCEL * FRAME_RATE)
# idx_mid_decel = int(peak_idx + T_MID_DECEL * FRAME_RATE)
idx_end = int(peak_idx + T_END * FRAME_RATE)
# idx_pre_150 = int(peak_idx + T_PREP_150 * FRAME_RATE)
idx_dur300ms = int(0.3*FRAME_RATE)
idx_dur250ms = int(0.25*FRAME_RATE)
idx_angSpd_max = int(peak_idx + (time_of_max_angSpd) * FRAME_RATE)

# %%
all_conditions = []
folder_paths = []
# get the name of all folders under root
for folder in os.listdir(root):
    if folder[0] != '.':
        folder_paths.append(root+'/'+folder)
        all_conditions.append(folder)

all_around_peak_data = pd.DataFrame()
all_cond1 = []
all_cond2 = []

# go through each condition folders under the root
for condition_idx, folder in enumerate(folder_paths):
    # enter each condition folder (e.g. 7dd_ctrl)
    for subpath, subdir_list, subfile_list in os.walk(folder):
        # if folder is not empty
        if subdir_list:
            # reset for each condition
            around_peak_data = pd.DataFrame()
            # loop through each sub-folder (experiment) under each condition
            for expNum, exp in enumerate(subdir_list):
                # angular velocity (angVel) calculation
                rows = []
                # for each sub-folder, get the path
                exp_path = os.path.join(subpath, exp)
                # get pitch                
                exp_data = pd.read_hdf(f"{exp_path}/bout_data.h5", key='prop_bout_aligned')#.loc[:,['propBoutAligned_angVel','propBoutAligned_speed','propBoutAligned_accel','propBoutAligned_heading','propBoutAligned_pitch']]
                exp_data = exp_data.assign(ang_speed=exp_data['propBoutAligned_angVel'].abs(),
                                            yvel = exp_data['propBoutAligned_y'].diff()*FRAME_RATE,
                                            xvel = exp_data['propBoutAligned_x'].diff()*FRAME_RATE,
                                            linear_accel = exp_data['propBoutAligned_speed'].diff(),
                                            ang_accel_of_SMangVel = exp_data['propBoutAligned_angVel'].diff(),
                                           )
                # assign frame number, total_aligned frames per bout
                exp_data = exp_data.assign(idx=int(len(exp_data)/total_aligned)*list(range(0,total_aligned)))
                
                # - get the index of the rows in exp_data to keep (for each bout, there are range(0:51) frames. keep range(20:41) frames)
                bout_time = pd.read_hdf(f"{exp_path}/bout_data.h5", key='prop_bout2').loc[:,['aligned_time']]
                # for i in bout_time.index:
                # # if only need day or night bouts:
                for i in day_night_split(bout_time,'aligned_time').index:
                    rows.extend(list(range(i*total_aligned+idxRANGE[0],i*total_aligned+idxRANGE[1])))
                exp_data = exp_data.assign(expNum = expNum,
                                           exp_id = condition_idx*100+expNum)
                around_peak_data = pd.concat([around_peak_data,exp_data.loc[rows,:]])
            # combine data from different conditions
            cond1 = all_conditions[condition_idx].split("_")[0]
            all_cond1.append(cond1)
            cond2 = all_conditions[condition_idx].split("_")[1]
            all_cond2.append(cond2)
            all_around_peak_data = pd.concat([all_around_peak_data, around_peak_data.assign(dpf=cond1,
                                                                                            condition=cond2)])
all_around_peak_data = all_around_peak_data.assign(
    time_ms = (all_around_peak_data['idx']-peak_idx)/FRAME_RATE*1000,
)
# %% tidy data
all_cond1 = list(set(all_cond1))
all_cond1.sort()
all_cond2 = list(set(all_cond2))
all_cond2.sort()

all_around_peak_data = all_around_peak_data.reset_index(drop=True)
peak_speed = all_around_peak_data.loc[all_around_peak_data.idx==peak_idx,'propBoutAligned_speed'],

grp = all_around_peak_data.groupby(np.arange(len(all_around_peak_data))//(idxRANGE[1]-idxRANGE[0]))
all_around_peak_data = all_around_peak_data.assign(
    peak_speed = np.repeat(peak_speed,(idxRANGE[1]-idxRANGE[0])),
    bout_number = grp.ngroup(),
                                )
all_around_peak_data = all_around_peak_data.assign(
                                    speed_bin = pd.cut(all_around_peak_data['peak_speed'],spd_bins,labels = np.arange(len(spd_bins)-1))
                                )
# %%
# cal bout features
features_all = pd.DataFrame()
all_around_peak_res =  pd.DataFrame()
expNum = all_around_peak_data['expNum'].max()
# jackknife_idx = jackknife_resampling(np.array(list(range(expNum+1))))
idx_list = np.array(list(range(expNum+1)))
for excluded_exp, idx_group in enumerate(idx_list):
    group = all_around_peak_data.loc[all_around_peak_data['expNum'].isin([idx_group])]
    yy = (group.loc[group['idx']==idx_post_bout,'propBoutAligned_y'].values - group.loc[group['idx']==idx_pre_bout,'propBoutAligned_y'].values)
    absxx = np.absolute((group.loc[group['idx']==idx_post_bout,'propBoutAligned_x'].values - group.loc[group['idx']==idx_pre_bout,'propBoutAligned_x'].values))
    epochBouts_trajectory = np.degrees(np.arctan(yy/absxx)) # direction of the bout, -90:90
    pitch_pre_bout = group.loc[group.idx==idx_pre_bout,'propBoutAligned_pitch'].values
    pitch_initial = group.loc[group.idx==idx_initial,'propBoutAligned_pitch'].values
    pitch_peak = group.loc[group.idx==int(peak_idx),'propBoutAligned_pitch'].values
    # pitch_mid_accel = group.loc[group.idx==int(idx_mid_accel),'propBoutAligned_pitch'].values
    traj_peak = group.loc[group['idx']==peak_idx,'propBoutAligned_instHeading'].values

    rot_all_l_accel = pitch_peak - pitch_initial

    bout_traj_peak = group.loc[group.idx==idx_angSpd_max,'propBoutAligned_instHeading'].values
    traj_deviation = bout_traj_peak-pitch_initial
    # rot_early_accel = pitch_mid_accel - pitch_pre_bout
    bout_features = pd.DataFrame(data={'pitch_pre_bout':pitch_pre_bout,
                                        'rot_all_l_accel': rot_all_l_accel,
                                       'pitch_initial':pitch_initial,
                                       'bout_traj_peak':bout_traj_peak,
                                       'traj_peak':traj_peak, 
                                       'traj_deviation':traj_deviation,
                                       'atk_ang':traj_peak-pitch_peak,
                                       'spd_peak': group.loc[group.idx==int(peak_idx),'propBoutAligned_speed'].values,
                                       })
    features_all = pd.concat([features_all,bout_features],ignore_index=True)
    


    grp = group.groupby(np.arange(len(group))//(idxRANGE[1]-idxRANGE[0]))
    null_initial_pitch = grp.apply(
        lambda group: group.loc[(group['idx']>(peak_idx-idx_dur300ms))&(group['idx']<(peak_idx-idx_dur250ms)), 
                                'propBoutAligned_pitch'].mean()
    )
    this_res = group.assign(
                                pitch_pre_bout = np.repeat(pitch_pre_bout,(idxRANGE[1]-idxRANGE[0])),
                                pitch_initial = np.repeat(pitch_initial,(idxRANGE[1]-idxRANGE[0])),
                                bout_traj_peak = np.repeat(bout_traj_peak,(idxRANGE[1]-idxRANGE[0])),
                                traj_peak = np.repeat(traj_peak,(idxRANGE[1]-idxRANGE[0])),
                                pitch_peak = np.repeat(pitch_peak,(idxRANGE[1]-idxRANGE[0])),
                                traj_deviation =  np.repeat(traj_deviation,(idxRANGE[1]-idxRANGE[0])),
                                absolute_pitch_change = group['propBoutAligned_pitch'] - np.repeat(null_initial_pitch,(idxRANGE[1]-idxRANGE[0])).values
                                )
    this_res = this_res.assign(
                                atk_ang = this_res['traj_peak']-this_res['pitch_peak'],
                                )
    all_around_peak_res = pd.concat([all_around_peak_res,this_res],ignore_index=True)
features_all = features_all.assign(
    direction = pd.cut(features_all['pitch_pre_bout'],[-90,separation_posture,90],labels = ['Nose-down', 'Nose-up'])
)

grp = all_around_peak_res.groupby(np.arange(len(all_around_peak_res))//(idxRANGE[1]-idxRANGE[0]))
all_around_peak_res = all_around_peak_res.assign(
    bout_number = grp.ngroup()
)
# %%
which_rotation = 'rot_all_l_accel'

# which_rotation = 'rot_narrow_ang_accel'
print("Figure 4: Scatter plot of traj. deviation vs acceleration rotation")

feature_to_plt = [which_rotation]
toplt = features_all

for feature in feature_to_plt:
    # # let's add unit
    # if 'spd' in feature:
    #     xlabel = feature + " (mm*s^-1)"
    # elif 'dis' in feature:
    #     xlabel = feature + " (mm)"
    # else:
    #     xlabel = feature + " (deg)"
    # plt.figure(figsize=(3,2))
    upper = np.percentile(toplt[feature], 99)
    lower = np.percentile(toplt[feature], 1)
    
    # g = sns.histplot(data=toplt, x=feature, 
    #                     bins = 20, 
    #                     element="poly",
    #                     #  kde=True, 
    #                     stat="density",
    #                     pthresh=0.05,
    #                     binrange=(lower,upper),
    #                     color='grey'
    #                     )
    # g.set_xlabel(xlabel)
    # sns.despine()
    # plt.savefig(fig_dir4+f"/{feature} distribution.pdf",format='PDF')
    # # plt.close()

# regression: attack angle vs accel rotation
to_plt = features_all.loc[features_all['spd_peak']>5]
BIN_WIDTH = 0.5
AVERAGE_BIN = np.arange(int(lower),int(upper),BIN_WIDTH)
# binned_df_dir = to_plt.groupby('direction').apply(
#     lambda g: distribution_binned_average_nostd(g,by_col=which_rotation,bin_col='traj_deviation',bin=AVERAGE_BIN)
# )
binned_df, _ = distribution_binned_average(to_plt,by_col=which_rotation,bin_col='traj_deviation',bin=AVERAGE_BIN)
binned_df.columns=['Accel rotation','traj_deviation']
# binned_df_dir.columns=['Accel rotation','traj_deviation']
# binned_df_dir = binned_df_dir.reset_index()
# %%
print("Figure 4: Distibution of traj. deviation and pitch change")
feature = 'traj_deviation'
plt.figure(figsize=(3,2))
upper = np.percentile(features_all[feature], 99.5)
lower = np.percentile(features_all[feature], 1)
xlabel = feature + " (deg)"
g = sns.histplot(
    data = features_all,
    x = feature,
    bins = 20, 
    element="poly",
    stat="probability",
    pthresh=0.05,
    binrange=(lower,upper),
    color='grey'
)
g.set_xlabel(xlabel)
sns.despine()
plt.savefig(os.path.join(fig_dir4,f"{feature} distribution.pdf"),format='PDF')

feature = 'rot_all_l_accel'
plt.figure(figsize=(3,2))
upper = np.percentile(features_all[feature], 99.5)
lower = np.percentile(features_all[feature], 1)
xlabel = "Pitch change from initial to peak (deg)"
g = sns.histplot(
    data = features_all,
    x = feature,
    bins = 20, 
    element="poly",
    stat="probability",
    pthresh=0.05,
    binrange=(-13,20),
    color='grey'
)
g.set_xlabel(xlabel)
sns.despine()
plt.savefig(os.path.join(fig_dir4,f"{feature} distribution.pdf"),format='PDF')

# %%
print("Figure 4: Pitch change towards trajectory")
xlabel = "Relative pitch change (deg)"
ylabel = 'Trajectory deviation (deg)'
 
g = sns.relplot(
    kind='scatter',
    data = to_plt.sample(frac=0.2),
    x = which_rotation,
    y = 'traj_deviation',
    # x_bins=np.arange(int(lower),int(upper),3),
    # x_ci=95,
    alpha=0.1,
    # hue='direction',
    # marker='+',
    linewidth = 0,
    color = 'grey',
    height=2.5,
    aspect=3/2,
)
# g.set(ylim=(-25,40))

g.set(ylim=(-10,20))
g.set(xlim=(lower,upper))
g.map(sns.lineplot,data=binned_df,
      x='Accel rotation',
      y='traj_deviation')
g.set_axis_labels(x_var = xlabel, y_var = ylabel)
sns.despine()
plt.savefig(fig_dir4+f"/traj deviation vs {which_rotation}.pdf",format='PDF')
r_val = stats.pearsonr(to_plt[which_rotation],to_plt['traj_deviation'])[0]
print(f"pearson's r = {r_val}")
# %%
# %%
# plot absolute pitch change
plt_features = 'absolute_pitch_change'
# sample bout groups
sample_bouts = np.random.choice(all_around_peak_res["bout_number"].unique(), 500)
df_sampled = all_around_peak_res.query('bout_number in @sample_bouts')

p = sns.relplot(
        data = df_sampled, x = 'time_ms', y = plt_features,
        kind = 'line',
        aspect=2, height=2, 
        # ci='sd',
        estimator=None,
        units = 'bout_number',
        alpha = 0.05
        )
p.map(
    plt.axvline, x=0, linewidth=1, color=".3", zorder=0
    )
p.set(xlim=(-250,200))
# p.map(
#     plt.axvline, x=time_of_peak_angSpd_mean, linewidth=2, color="green", zorder=0
#     )
plt.savefig(os.path.join(fig_dir4, f"{plt_features}_timeSeries sampled.pdf"),format='PDF')

# %%