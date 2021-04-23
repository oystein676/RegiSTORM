import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import pathlib as pl
import os
import glob
from sklearn.neighbors import NearestNeighbors
import time
from joblib import Parallel, delayed
import scipy.spatial as spatial
import itertools

# Other functions
#Functions for reading CSV files
def setupPath(processed = None):
    code_pth = pl.Path(os.getcwd())
    base_pth = code_pth.parent
    if processed is None:
        data_pth = base_pth / 'Data'
    else:
        data_pth = base_pth / processed
    rslt_pth = base_pth / 'Results'
    rslt_pth.mkdir(parents=True, exist_ok=True)
    return code_pth, base_pth, data_pth, rslt_pth


def Counter(dfF1, DataFrame, tolerance):
    point_tree = spatial.cKDTree(DataFrame[['x [nm]', 'y [nm]']].to_numpy())
    # This finds the index of all points within distance 100 of [1.5,2.5].
    XY_in_R=point_tree.query_ball_point(dfF1, tolerance, return_length=True)
    return XY_in_R         
      
#Functions for identifying fiducials
def SumVar(dfF1, df, tolerance):
    start = time.time()
    Output=Parallel(n_jobs=4)(delayed(Counter)(dfF1,  df.loc[df['frame']==i], tolerance) for i in df.frame.unique().astype(int))
    Cnt=[]
    for items in zip(*Output):
        Cnt.append(np.asarray(items))
    Var=[items.var() for items in Cnt]
    Sum=[items.sum() for items in Cnt]
    MN=[items.mean() for items in Cnt]
    stop = time.time()
    duration = stop-start
    return  Var, Sum, MN, duration

def ClusterDefinition(df, Sum, MN, Var, VarLim, MeanTol, Fiducial_Mode='yes'):
    if Fiducial_Mode == 'Fiducial':
        Var_Idx=[Idx for Idx, Var in enumerate(Var) if Var <= float(VarLim)]
        Mean_Idx=[Idx for Idx, Mean in enumerate(MN) if Mean>= float(MeanTol)]
        Stable_Idx=list(set(Mean_Idx).intersection(Var_Idx))
        Var2=[Var[i] for i in Stable_Idx]
        MN2=[MN[i] for i in Stable_Idx]
        Sum2=[Sum[i] for i in Stable_Idx]
        Stable_Pts=df.iloc[Stable_Idx]
        Stable_Pts.insert(9, "Frames localized", Sum2)
        Stable_Pts.insert(10, "Mean localized", MN2)
        Stable_Pts.insert(11, "Variance localized", Var2)
    elif Fiducial_Mode == 'Cluster':
        # Sorted value
        srt_val = sorted(Sum)
        # Sorting indices (descending)
        srt_idx = np.argsort(Sum)[::-1]
        Stable_Pts=df.iloc[srt_idx[:25]]
        Dec_Srt_Val=srt_val[::-1]
        Stable_Pts.insert(9, "Frames localized", Dec_Srt_Val[0:len(Stable_Pts)])
    else:
        print('Failed to identify mode')
        Stable_Pts=0
    return Stable_Pts

def Delete_Fiducials(Channel, Fiducials, Tolerance):
    Fiducials=Fiducials[['x [nm]', 'y [nm]']].to_numpy() 
    Channel_Coordinates=Channel[['x [nm]', 'y [nm]']].to_numpy()
    point_tree = spatial.cKDTree(Channel_Coordinates)
    Index_2_Del=point_tree.query_ball_point(Fiducials, Tolerance)
    Index_2_Del=list(itertools.chain.from_iterable(Index_2_Del))
    Channel=Channel.drop(Channel.index[Index_2_Del])
    return Channel, Index_2_Del

#Identifying fiducials - Returns a list with the identified fiduicals/cluster for each channel.
def Fiducial_Identification(channels, Fiducial_Size, Fiducial_Mode, VarLim, MeanTol, FrameInterval, window1):
    Most_Obs_Pts=[]
    for idx, channel in enumerate(channels):
        start1 = time.time()
        Start=FrameInterval[idx][0]
        End=FrameInterval[idx][1]
        print('Identifying the fiducials in: ', channel)
        window1["textOutput"].Update(value='Identifying the fiducials in: ' + channel + "\n", append=True)
        df=channels[channel]
        if End == 'end':
            End = df['frame'].max()
        df=channels[channel].loc[(channels[channel]['frame']>float(Start)) & (channels[channel]['frame']<float(End))]
        is_frame_1 = df ['frame'] == df['frame'].value_counts().idxmax()
        print('# potential fiducials: ', len(df[is_frame_1]))
        window1["textOutput"].Update(value='# potential fiducials: ' + str(len(df[is_frame_1])) + "\n", append=True)

        # process
        VarFrames, NumPts, MeanFrames, TimeDuration= SumVar(df[is_frame_1][['x [nm]', 'y [nm]']].to_numpy(), df, Fiducial_Size)

        #Sorted value
        Stable_Pts=ClusterDefinition(df[is_frame_1], NumPts, MeanFrames, VarFrames, VarLim, MeanTol, Fiducial_Mode)
        Most_Obs_Pts.append(Stable_Pts)
        stop1 = time.time()
        duration1 = stop1-start1
        print('# Fiducials identified: ', len(Stable_Pts))
        window1["textOutput"].Update(value='# Fiducials identified: ' + str(len(Stable_Pts)) + "\n", append=True)
        print('Time for processing channel ', duration1, ' seconds')
        window1["textOutput"].Update(value='Time for processing channel ' + str(duration1) + ' seconds' + "\n", append=True)
    return Most_Obs_Pts

#ICP 
def best_fit_transform(A_BF, B_BF):


    # get number of dimensions
    m = max(A_BF.shape[1], B_BF.shape[1])

    # translate points to their centroids
    centroid_A = np.mean(A_BF, axis=0)
    centroid_B = np.mean(B_BF, axis=0)
    AA = A_BF - centroid_A
    BB = B_BF - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)


    # translation
    t = centroid_B.T - np.dot(R,centroid_A.T)

    # homogeneous transformation
    T = np.identity(m+1)
    T[:m, :m] = R
    T[:m, m] = t

    return T, R, t

def Outliers(data, m=2):
    m=int(m)
    dist_out=data[abs(data-np.mean(data))>m*np.std(data)]
    idx_out=np.where(abs(data-np.mean(data))>m*np.std(data))
    #print('Distance mean: ', np.mean(data), ' nm. {m} std: ', m*np.std(data), ' nm.')
    return dist_out, idx_out[0]


def nearest_neighbor(src, dst):

    neigh = NearestNeighbors(n_neighbors=1)
    neigh.fit(dst)
    distances, indices = neigh.kneighbors(src, return_distance=True)
    return distances.ravel(), indices.ravel()


def icp(A, B, window1, max_iterations=20, tolerance=1, RegTol=1):
    print('Starting ICP transformation...')
    window1["textOutput"].Update(value='Starting ICP transformation...' + "\n", append=True)
    #assert A.shape == B.shape

    # get number of dimensions
    m = max(A.shape[1], B.shape[1])
    n = max(A.shape[0], B.shape[0])
    
    # make points homogeneous, copy them to maintain the originals
    src = np.ones((m+1,A.shape[0]))
    dst = np.ones((m+1,B.shape[0]))
    src[:m,:(len(A))] = np.copy(A.T)
    dst[:m,:(len(B))] = np.copy(B.T)



    prev_error = 0
    distances, indices = nearest_neighbor(src[:m,:].T, dst[:m,:].T)
    Ind_Mod=indices.T
    
    for i in range(max_iterations):
        distances, indices = nearest_neighbor(src[:m,:].T, dst[:m,:].T)
        Ind_Mod=indices.T
        
        # find the nearest neighbors between the current source and destination points
        OutDist,idx_2_del=Outliers(distances, m=RegTol)

        
        Ind_Modified=np.delete(Ind_Mod, idx_2_del)
        distances=np.delete(distances, idx_2_del) 
        
        indices=Ind_Modified
        A_Idx=list(range(len(A)))
        A_Idx=np.delete(A_Idx, idx_2_del)
        
        # compute the transformation between the current source and nearest destination points
        T,_,_ = best_fit_transform(src[:m,A_Idx].T, dst[:m,indices].T)

        # update the current source
        src = np.dot(T, src)

        # check error
        mean_error = np.mean(distances)
        print('Iteration ', i, ' Mean error = ', mean_error)
        window1["textOutput"].Update(value='Iteration '+ str(i)+ ' Mean error = ' + str(mean_error) + "\n", append=True)
        if np.abs(prev_error - mean_error) < tolerance:
            break
        prev_error = mean_error

    # calculate final transformation
    T,R,t = best_fit_transform(A, src[:m,:].T)

    return T, distances, i, src, R, t

def Channel_Registration(Channels_CSV, Channel_Name, Most_Obs_Pts, Registration_Tolerance, MeanTol, ModeFid, Fiducial_Size, Loop_Idx, Goal_Idx, B,  ResultPath, ResultSuffix, Fiducial_Mode, window1):

    for Idx in Loop_Idx:
        print('Channel being transformed: ', Channel_Name[Idx])
        window1["textOutput"].Update(value='Channel being transformed: ' + Channel_Name[Idx] + "\n", append=True)
        A=np.array([Most_Obs_Pts[Idx]['x [nm]'].to_numpy(), Most_Obs_Pts[Idx]['y [nm]'].to_numpy()]).T
        T, D, i, src, R, t = icp(A, B,window1, RegTol= Registration_Tolerance)
        print('R: ', R)
        window1["textOutput"].Update(value='R: ' + str(R) + "\n", append=True)
        print('t: ', t)
        window1["textOutput"].Update(value='t: ' + str(t) + "\n", append=True)

        AA=np.array([Channels_CSV[Channel_Name[Idx]]['x [nm]'].to_numpy(), Channels_CSV[Channel_Name[Idx]]['y [nm]'].to_numpy()]).T
        mm=AA.shape[1]
        AA_SRC= np.ones((mm+1,AA.shape[0]))
        AA_SRC[:mm,:] = np.copy(AA.T)
        Transform=np.identity(mm+1)
        Transform[:mm, :mm] = R
        Transform[:mm, mm] = t

        AA_Trans=np.dot(Transform, AA_SRC)
        AA_Trans=AA_Trans[:2,:]
        AA_Trans_DF=pd.DataFrame({'x [nm]': AA_Trans[0], 'y [nm]': AA_Trans[1]})

        Channel_Transformed=Channels_CSV[Channel_Name[Idx]].copy()
        Channel_Transformed['x [nm]']=AA_Trans_DF['x [nm]']
        Channel_Transformed['y [nm]']=AA_Trans_DF['y [nm]']


        #Do the same transformation to just the fiducials:
        mm=A.shape[1]
        A_SRC= np.ones((mm+1,A.shape[0]))
        A_SRC[:mm,:] = np.copy(A.T)
        TransformFid=np.identity(mm+1)
        TransformFid[:mm, :mm] = R
        TransformFid[:mm, mm] = t

        A_Trans=np.dot(TransformFid, A_SRC)
        A_Trans=A_Trans[:2,:]
        A_Trans_DF=pd.DataFrame({'x [nm]': A_Trans[0], 'y [nm]': A_Trans[1]})

        Channel_TransformedFid=Most_Obs_Pts[Idx].copy()
        Channel_TransformedFid['x [nm]']=A_Trans_DF['x [nm]'].values
        Channel_TransformedFid['y [nm]']=A_Trans_DF['y [nm]'].values


        #Quantification of the difference before and after transformation + histogram
        Corrected=Channel_Transformed[['x [nm]','y [nm]']]
        Uncorrected_df=Channels_CSV[Channel_Name[Idx]]
        Uncorrected=Uncorrected_df[['x [nm]','y [nm]']]
        Goal_df=Channels_CSV[Channel_Name[Goal_Idx[0]]]
        Goal=Goal_df[['x [nm]','y [nm]']]

        #Deleting the fiducials + area around 
        if Fiducial_Mode == "Fiducial":    
            if ModeFid == True:
                Channel_Transformed, Idx2Del=Delete_Fiducials(Channel_Transformed, Channel_TransformedFid, float(Fiducial_Size))


        #Saving corrected files
        CH1=os.path.join(ResultPath, Channel_Name[Idx][:-4] + ResultSuffix + '.csv')
        Channel_Transformed.to_csv(''.join(CH1))
        

        #Saving corrected fiducials
        if Fiducial_Mode == "Fiducial":
            CSV_name=os.path.join(ResultPath, Channel_Name[Idx] + ' Fiducial transformed.csv')
            Channel_TransformedFid.to_csv(''.join(CSV_name))
        
            print('The transformed channels has been saved...')
            window1["textOutput"].Update(value='The transformed channels has been saved...' + "\n", append=True)
            if ModeFid == True:
                Channel_Transformed=Channels_CSV[Channel_Name[Goal_Idx[0]]]
                Channel_Transformed, Idx2Del=Delete_Fiducials(Channel_Transformed, Most_Obs_Pts[Goal_Idx[0]], Fiducial_Size)
                CH2=os.path.join(ResultPath, Channel_Name[Goal_Idx[0]][:-4] + ResultSuffix + '.csv')
                Channel_Transformed.to_csv(''.join(CH2))
                print('Fiducials have been deleted from the images...')
                window1["textOutput"].Update(value='Fiducials have been deleted from the images...' + "\n", append=True)

    return 

def MCR(Job, window1):
    #1. Define Job Variables
    print("Starting Job: ", Job["name"])
    window1["textOutput"].Update(value="Starting Job: " + Job["name"] + "\n", append=True)
    #Channel_Name=Job['File Names'] #Names of the channels in order
    Fiducial_Size=Job['fiducialSize'] #Tolerance of the fiducials/clusters localisation within a channel [nm]
    VarLim=Job['varianceLimit'] #Maximum variance before point is considered unstable
    MeanTol=Job['meanTol']
    Fiducial_Mode=Job['mode'] #Whether the algorithm should look for fiducials [Yes] or clusters [No]
    RegTol=Job['registrationTolerance'] #How many standard deviation the confidence interval should be for distances to transform after. 
    ModeFid=Job['deleteFiducialsAfter']
    FrameInterval=Job['frameIntervals'] #Which is the starting frame of the channel
    
    
                
    #2. Identify file paths and Load relevant CSVs
    channels={}
    Channel_Name=[]
    for n, path in enumerate(Job['fileList']):
        name=os.path.basename(os.path.normpath(Job['File Names'][n]))
        channels.update({name: pd.read_csv(path)})
        
        Channel_Name.append(name)
    Channels_CSV={}
    for idx, channel in enumerate(channels):
        df=channels[channel]
        Channels_CSV.update({Channel_Name[idx]: df})
        
    #3. Identifying the Fiducials
    Most_Obs_Pts=Fiducial_Identification(channels, Fiducial_Size, Fiducial_Mode, VarLim, MeanTol, FrameInterval, window1)
    
    #4. Save the coordinates of the untransformed fiducials
    if Fiducial_Mode == "Fiducial":
        for n, name in enumerate(Channel_Name):
            ToJoin=[name, ' Fiducial untransformed.csv']
            CHname=' '.join(ToJoin)
            CSV_name=os.path.join(Job['resultsFolder'], CHname)
            Most_Obs_Pts[n].to_csv(''.join(CSV_name))
        print('The untransformed fiducials observations are saved')
        window1["textOutput"].Update(value='The untransformed fiducials observations are saved' + "\n", append=True)

    #5:
    #Split the channels into channels to be transformed and which to transform to
    Loop_Idx=[i for i,x in enumerate(Channel_Name) if x!=os.path.basename(os.path.normpath(Job['selected']))]
    Goal_Idx=[i for i,x in enumerate(Channel_Name) if x==os.path.basename(os.path.normpath(Job['selected']))]
    
    
    #Define the goal og the transformation
    B=np.array([Most_Obs_Pts[Goal_Idx[0]]['x [nm]'].to_numpy(), Most_Obs_Pts[Goal_Idx[0]]['y [nm]'].to_numpy()]).T
    
    #6. MCR
    Channel_Registration(Channels_CSV, Channel_Name, Most_Obs_Pts, RegTol, MeanTol, ModeFid, Fiducial_Size, Loop_Idx, Goal_Idx, B,  Job['resultsFolder'], Job['resultsSuffix'], Fiducial_Mode, window1)
    
    print("... Job: ", Job["name"], " Finished.") 
    window1["textOutput"].Update(value="... Job: " + Job["name"] + " Finished." + "\n", append=True)      
