from datetime import datetime
import joblib
import sys
from matplotlib import pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, RationalQuadratic, DotProduct, WhiteKernel
from scipy.interpolate import interp1d
from modelDefinition import *

colors  = {'0.03':['tab:cyan',(0,(3,5,3,5))]
          ,'0.04':['tab:cyan',(0,(3,1,1,1,1,1))]
          ,'0.05':['tab:cyan',(0,(5,1))]
          ,'0.06':['tab:cyan',(0,())]
          ,'0.07':['tab:blue',(0,(3,5,3,5))]
          ,'0.08':['tab:blue',(0,(3,1,1,1,1,1))]
          ,'0.09':['tab:blue',(0,(5,1))]
          ,'0.10':['tab:blue',(0,())]
          ,'0.11':['tab:orange',(0,(3,5,3,5))]
          ,'0.12':['tab:orange',(0,(3,1,1,1,1,1))]
          ,'0.13':['tab:orange',(0,(5,1))]
          ,'0.14':['tab:orange',(0,())]
          ,'0.15':['tab:red',(0,(3,5,3,5))]
          ,'0.16':['tab:red',(0,(3,1,1,1,1,1))]
          ,'0.17':['tab:red',(0,(5,1))]
          ,'0.18':['tab:red',(0,())]}

###########################################################

### stresses_normalized_25
##hTrain = [0.04,0.08,0.10,0.12,0.16]
##rTrain = [32,42,47,52,62]
##testID = 'stresses_normalized_25'

## stresses_normalized
##hTrain = [0.04,0.08,0.12,0.16]
##rTrain = [32,42,52,62]
##testID = 'adimensional_stresses_normalized'

## stresses_normalized
#hTrain = [0.04,0.08,0.12,0.16]
#rTrain = [32,42,52,62]
#testID = 'model'

## stresses_normalized
#hTrain = [0.04,0.08,0.12,0.16]
#rTrain = [32,42,52,62]
#testID = 'model'

##hTrain = [0.04,0.08]
##rTrain = [32,42]

#devPairs = np.array([[0.06,37],[0.14,47]])
#testPairs = np.array([[0.06,47],[0.14,57]])

nCpu = 12


# stresses_normalized
hTrain = [0.04]
rTrain = [52,62,72,82,92]
testID = 'long'

devPairs = np.array([[0.04,52],[0.04,92]])
testPairs = np.array([[0.04,62],[0.04,82]])

QoIs = ['u','uu','vv','ww','uv']
#QoIs = ['Iu','Iv','Iw','Iuv']
#QoIs = ['Iuv']

PFDatabase = '../../TIGTestMatrixLong'

setToPlot = 'Test'


###########################################################

xModels = eval(sys.argv[1])
mode    = sys.argv[2]

trainPairs = np.zeros((len(hTrain)*len(rTrain),2))
cont=0
for h in hTrain:
    for r in rTrain:
        trainPairs[cont,:] = [h, r]
        cont+=1

features = ['y','h','r']

yMax= 1.0

if mode == 'Gridsearch':

    for x in xModels:
        
        trainPoints = {'h':trainPairs[:,0],'r':trainPairs[:,1],'x':[x]}
        devPoints = {'h':devPairs[:,0],'r':devPairs[:,1],'x':[x]}
        testPoints = {'h':testPairs[:,0],'r':testPairs[:,1],'x':[x]}
        
        prefix = str(str(x)+'_').replace('.','p')
        directory = prefix+testID

        for QoI in QoIs:

            gp = gaussianProcess(trainPoints, devPoints, testPoints, yMax, PFDatabase, np.linspace(0.01,1.0,100))
            
            try:
                os.mkdir('../GPRModels/'+directory+'_'+QoI)
            except:
                print('Directory already exist')
            
                    
            with open('../GPRModels/'+directory+'_'+QoI+'.dat', 'w+') as out:
                now = datetime.now()
                out.write('\n'*10+'Gridsearch performed on ' + str(now.strftime("%d %m %Y, %H:%M:%S"))+ '\n'*10)
                
            _ = joblib.Parallel(n_jobs=nCpu)(joblib.delayed(gp.gridsearch)(seed, features, directory, QoI)
                                    for seed in range(0,12))

#############################################################


elif mode == 'Plot':

    for x in xModels:

        my_dpi = 100
        plt.figure(figsize=(2260/my_dpi, 1300/my_dpi), dpi=my_dpi)
        cont=1
                
        trainPoints = {'h':trainPairs[:,0],'r':trainPairs[:,1],'x':[x]}
        devPoints = {'h':devPairs[:,0],'r':devPairs[:,1],'x':[x]}
        testPoints = {'h':testPairs[:,0],'r':testPairs[:,1],'x':[x]}
        
        gp = gaussianProcess(trainPoints, devPoints, testPoints, yMax, PFDatabase, np.linspace(0.01,1.0,100))

        for QoI in QoIs:
            
            prediction = []
            target = []
            
            #refTrainData = trainPairs
            #refDevData = devPairs
        
            for i in range(trainPairs.shape[0]):
                
                h=trainPairs[i,0]
                r=trainPairs[i,1]
                
                trainData = loadData([h], [x], [r], yMax, False, PFDatabase, np.linspace(0.01,1.0,100))
                
                prefix = str(str(x)+'_').replace('.','p')
                directory = prefix+testID
                
                model = '../GPRModels/'+directory+'_'+QoI+'.pkl'
                
                y_mean_train = gp.predict(model,trainData,features)
                
                plt.subplot(2,5,cont)
                plt.plot(trainData[QoI],trainData['y'],color='tab:grey')
                plt.plot(y_mean_train['y_model'],trainData['y'],label = 'x='+str(x)+'m, h='+str(h)+'m, r='+str(r))
                plt.ylabel('y/H')
                plt.xlabel(QoI +' Train')
                
            if setToPlot == 'Dev':
                withheld = devPairs
            elif setToPlot=='Test':
                withheld = testPairs
                        
            for i in range(withheld.shape[0]):
                
                h=withheld[i,0]
                r=withheld[i,1]
                
                withheldData = loadData([h], [x], [r], yMax, False, PFDatabase, np.linspace(0.01,1.0,100))
                
                prefix = str(str(x)+'_').replace('.','p')
                directory = prefix+testID+'_'+QoI
                
                model = '../GPRModels/'+directory+'.pkl'
                
                y_mean_dev = gp.predict(model,withheldData,features)
                
                target.extend(withheldData[QoI].to_numpy()) 
                prediction.extend(y_mean_dev['y_model'].to_numpy())
                
                #print(withheldData)
                #print(y_mean_dev)
                #print(h,r)
                #input()
                
                #print(np.linalg.norm((withheldData[QoI]-y_mean_dev['y_model'])/withheldData[QoI]))
                #print(np.linalg.norm(withheldData[QoI]-y_mean_dev['y_model']))
                #print(QoI,h,r)
                
                plt.subplot(2,5,cont+5)
                plt.plot(withheldData[QoI],withheldData['y'],color='tab:grey')
                if i == 0:
                    plt.fill_betweenx(withheldData['y'], withheldData[QoI]*0.9, withheldData[QoI]*1.1, color='tab:grey', alpha=0.3,label=r'Reference $\pm$10%')
                else:
                    plt.fill_betweenx(withheldData['y'], withheldData[QoI]*0.9, withheldData[QoI]*1.1, color='tab:grey', alpha=0.3)
                plt.plot(y_mean_dev['y_model'],withheldData['y'],label = 'x='+str(x)+'m, h='+str(h)+'m, r='+str(r))
                plt.ylabel('y/H')
                plt.xlabel(QoI +' '+setToPlot)
                
            cont +=1
            
            #print(np.array(prediction))
            #print(np.array(target))
            #print((np.array(prediction)-np.array(target))/np.array(target))
            #print(QoI + ' Relative RMSE: ' +str(np.linalg.norm((np.array(prediction)-np.array(target))/np.array(target))))
            #print(QoI + ' Absolute RMSE: ' +str(np.linalg.norm(np.array(prediction)-np.array(target))))
            ##input()

        plt.legend()
        plt.savefig('../RegressionPlots/'+prefix+testID+'_'+setToPlot+'.png', bbox_inches='tight')
        plt.show()
        plt.close('all')