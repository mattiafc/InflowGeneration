import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from modelDefinition import *

###########################################################

PFDatabase = './GPRDatabase'

#directories = {'../../CatherineABLs/LRB_Cat1_scale1to25/':[r'$U_{\infty}=45m/s$, U=3U_0',[25000,150000],'tab:blue',1.0]
              #,'../../CatherineABLs/LRB_Cat1_scale1to25_times3/':[r'$U_{\infty}=15m/s$, L = 3L_0',[25000,75000],'tab:orange',3.0]
              #,'../../TIGTestMatrixLong/PFh0.04u15r72/':[r'Reference r=72',[25000,75000],'tab:grey',1.0]}
#reference = {'fName':'LRB_Cat1_scale1to25','h':0.04,'r':75,'alpha':0.36,'k':1.36,'x':3.3,'hMatch':0.666}

#directories = {'../../CatherineABLs/LRB_Cat1_geometric_1to50/':[r'$U_{\infty}=15m/s$, 1to50',[25000,100000],'tab:orange',0.42857143*0.42]
              #,'../../CatherineABLs/LRB_Cat1_geometric_1to25/':[r'$U_{\infty}=15m/s$, 1to25',[25000,75000], 'tab:blue',0.857142860*0.42]
              #,'../../CatherineABLs/LRB_Cat1_geometric_1to10/':[r'$U_{\infty}=15m/s$, 1to10',[25000,100000],'tab:cyan',2.1428572*0.42]
              #,'../../CatherineABLs/LRB_Cat1_geometric_1to1/': [r'$U_{\infty}=15m/s$, 1to1', [25000,100000],'tab:purple',21.428572*0.42]
              #,'../../TIGTestMatrixLong/PFh0.06u15r57/':[r'Reference r=57',[25000,75000],'tab:grey',0.42]}

#directories = {'../../CatherineABLs/LRB_Cat1_geometric_1to50/':[r'$U_{\infty}=15m/s$, 1to50',[25000,100000],'tab:orange',0.42857143*0.42]
              #,'../../CatherineABLs/LRB_Cat1_geometric_1to21/':[r'$U_{\infty}=15m/s$, 1to21',[25000,100000],'tab:blue',1.0*0.42]
              #,'../../CatherineABLs/LRB_Cat1_geometric_1to10/': [r'$U_{\infty}=15m/s$,1to10', [25000,100000],'tab:cyan',2.1428572*0.42]
              #,'../../CatherineABLs/LRB_Cat1_geometric_1to1/': [r'$U_{\infty}=15m/s$, 1to1', [25000,100000],'tab:purple',21.428572*0.42]}
#reference = {'fName':'LRB_Cat1','h':0.06,'r':54,'alpha':0.42,'k':1.35,'x':3.3,'hMatch':0.666}

directories = {'../../CatherineABLs/MRB_Cat2_geometric_1to1/': [r'$U_{\infty}=15m/s$,1to1', [25000,100000],'tab:cyan',71.428571*0.42]
              ,'../../CatherineABLs/MRB_Cat2_geometric_1to10/': [r'$U_{\infty}=15m/s$, 1to10', [25000,100000],'tab:purple',7.1428571*0.42]
              ,'../../CatherineABLs/MRB_Cat2_geometric_1to25/': [r'$U_{\infty}=15m/s$, 1to25', [25000,100000],'tab:blue',2.85714284*0.42]
              ,'../../CatherineABLs/MRB_Cat2_geometric_1to50/': [r'$U_{\infty}=15m/s$, 1to50', [25000,100000],'tab:orange',1.42857142*0.42]
              ,'../../CatherineABLs/MRB_Cat2_geometric_1to100/': [r'$U_{\infty}=15m/s$, 1to100', [25000,100000],'tab:brown',0.71428571*0.42]}
reference = {'fName':'MRB_Cat2','h':0.04,'r':92,'alpha':0.42,'k':1.47,'x':3.0,'hMatch':0.666}



#fName = 'themisABL'
#directories = {'../../InflowValidation/ThemisShortPFh0.06u15r87/':[r'$U_{\infty}=26m/s$',[25000,75000],'tab:blue',1.0]}
#reference = {'fName':'themisABL','h':0.06,'r':87,'alpha':0.4,'x':0.9,'hMatch':0.714}
##prefix = '0p9_'
yMax = 0.42*1.5

#yMax = 0.9
adimensional = True

###########################################################

intensitiesModelID = 'intensities'
uncertainty = False

features = ['y','h','r']

xList = [0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.4,2.7,3.0,3.3,3.6,4.0,5.0,6.0,7.0,9.0,11.0,13.0]

hTrain = [0.04,0.08,0.12,0.16]
rTrain = [52,62,72,82,92]

devPairs = np.array([[0.06,57],[0.06,87],[0.14,67],[0.14,77]])
testPairs = np.array([[0.06,67],[0.06,77],[0.14,57],[0.14,87]])

trainPairs = np.zeros((len(hTrain)*len(rTrain),2))
cont=0
for hTemp in hTrain:
    for rTemp in rTrain:
        trainPairs[cont,:] = [hTemp, rTemp]
        cont+=1
        
fit_features = pd.DataFrame()
fit_features['y'] = np.linspace(0.01,1.0,2000)
fit_features['x'] = reference['x']
fit_features['h'] = reference['h']
fit_features['r'] = reference['r']
fit_features['alpha'] = reference['alpha']

trainPoints = {'h':trainPairs[:,0],'r':trainPairs[:,1],'x':[reference['x']]}
devPoints = {'h':devPairs[:,0],'r':devPairs[:,1],'x':[reference['x']]}
testPoints = {'h':testPairs[:,0],'r':testPairs[:,1],'x':[reference['x']]}

gp = gaussianProcess(trainPoints, devPoints, testPoints, yMax, PFDatabase)

prefix = str(str(reference['x'])+'_').replace('.','p')
directory = prefix+intensitiesModelID
    
ref_abl = pd.read_csv('TestCases/'+reference['fName']+'.dat',sep=',')
header = list(ref_abl.columns)
idx = np.argmax(ref_abl['y'].to_numpy())

yref = ref_abl['y'].iloc[idx]*1.0

ref_abl['y'] = ref_abl['y']/yref
ref_abl['u'] = ref_abl['u']
  
model = '../GPRModels/'+directory+'_u.pkl'
y_mean = gp.predict(model,fit_features,features,'u')
y_mean = y_mean.loc[y_mean['y']<=reference['alpha']*np.max(y_mean['y'])]
y_mean['y'] = y_mean['y']/(y_mean['y'].max())
#y_mean['y_model'] = y_mean['y_model']

U_ABL_dim = (interp1d(ref_abl['y'], ref_abl['u'])(reference['hMatch'])).item()
U_TIG_dim = (interp1d(y_mean['y'], y_mean['y_model'])(reference['hMatch'])).item()

Uscaling = U_ABL_dim/(U_TIG_dim)

my_dpi = 100
plt.figure(figsize=(2260/my_dpi, 1300/my_dpi), dpi=my_dpi)


for fold in directories:
    
    cont=1
        
    resultsDF = pd.DataFrame()

    avg_u = np.loadtxt(fold+prefix+'avg_u.'+str(directories[fold][1][1]).zfill(8)+'.collapse_width.dat',skiprows = 3)

    Umag = np.loadtxt(fold+prefix+'mag_u.'+str(directories[fold][1][1]).zfill(8)+'.collapse_width.dat',skiprows = 3)

    rms_u = np.loadtxt(fold+prefix+'rms_u.'+str(directories[fold][1][1]).zfill(8)+'.collapse_width.dat',skiprows = 3)
    rms_v = np.loadtxt(fold+prefix+'rms_v.'+str(directories[fold][1][1]).zfill(8)+'.collapse_width.dat',skiprows = 3)
    rms_w = np.loadtxt(fold+prefix+'rms_w.'+str(directories[fold][1][1]).zfill(8)+'.collapse_width.dat',skiprows = 3)

    uv = np.loadtxt(fold+prefix+'uv.'+str(directories[fold][1][1]).zfill(8)+'.collapse_width.dat',skiprows = 3)
    
    if adimensional == True:
        U_adim = (interp1d(avg_u[:,3],avg_u[:,5])(reference['hMatch']*yref*directories[fold][3])).item()
    else:
        U_adim = 1.0
    
    resultsDF['y'] = avg_u[:,3]/(yref*directories[fold][3])
    resultsDF['u'] = avg_u[:,5]/U_adim
    resultsDF['Iu'] = rms_u[:,5]/Umag[:,5]
    resultsDF['Iv'] = rms_v[:,5]/Umag[:,5]
    resultsDF['Iw'] = rms_w[:,5]/Umag[:,5]
    
    for QoI in ['u','Iu','Iv','Iw']:
        
        plt.subplot(1,4,cont)
            
        plt.plot(resultsDF[QoI],resultsDF['y'], label = directories[fold][0], color=directories[fold][2],linewidth=2)
        plt.ylim([0,1.0])

        cont += 1
cont = 1
for QoI in ['u','Iu','Iv','Iw']:
    plt.subplot(1,4,cont)
    
    model = '../GPRModels/'+directory+'_'+QoI+'.pkl'
    
    y_mean = gp.predict(model,fit_features,features,QoI)
    y_mean = y_mean.loc[y_mean['y']<=reference['alpha']*np.max(y_mean['y'])]
    y_mean['y'] = y_mean['y']/(y_mean['y'].max())
    
    if QoI == 'u':
        if adimensional == True:
            y_mean['y_model'] = y_mean['y_model']/U_TIG_dim
            y_mean['y_std'] = y_mean['y_std']/U_TIG_dim
            ref_abl[QoI] = ref_abl[QoI]/U_ABL_dim
        else:
            y_mean['y_model'] = y_mean['y_model']*Uscaling
            y_mean['y_std'] = y_mean['y_std']*Uscaling
    
    plt.plot(y_mean['y_model'],y_mean['y'],label=r'Optimization prediction, $U_{\infty}=15m/s$',linewidth=2,color='tab:green')
                    
    if (QoI in header):
        plt.plot(ref_abl[QoI],ref_abl['y'],color='tab:red',label='Target',linewidth=2)
        plt.fill_betweenx(ref_abl['y'], ref_abl[QoI]*0.9, ref_abl[QoI]*1.1, color='tab:red', alpha=0.2,label=r'Reference $\pm$10%')
    cont +=1
    
plt.legend()
plt.savefig('../RegressionPlots/AllQoIs.png', bbox_inches='tight')
# plt.show()