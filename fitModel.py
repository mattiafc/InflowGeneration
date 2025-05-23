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

# Define a function that processes each group
def RMSE_compute(group):
    
    all_les = np.concatenate(group['LES'].values)
    all_gpr = np.concatenate(group['GPR'].values)
    print()
    
    return pd.Series({'RMSE': np.sqrt(np.sum((all_les-all_gpr)**2) / len(all_les))})

###########################################################


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

if __name__ == '__main__':

    nCpu = 128

    PFDatabase = './GPRDatabase/'

    # stresses_normalized
    hTrain = [0.04,0.08,0.12,0.16]
    rTrain = [52,62,72,82,92]

    devPairs = np.array([[0.06,57],[0.06,87],[0.14,67],[0.14,77]])
    testPairs = np.array([[0.06,67],[0.06,77],[0.14,57],[0.14,87]])

    #QoIs = ['u','Iu','Iv','Iw']
    #testID = 'intensities_high_noA'
    
    QoIs = ['u','uu','vv','ww','uv']
    testID = 'inflow_stresses'

    setToPlot = 'Test'

    yMax= 1.5

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

    if mode == 'Gridsearch':

        for x in xModels:
            
            trainPoints = {'h':trainPairs[:,0],'r':trainPairs[:,1],'x':[x]}
            devPoints = {'h':devPairs[:,0],'r':devPairs[:,1],'x':[x]}
            testPoints = {'h':testPairs[:,0],'r':testPairs[:,1],'x':[x]}
            
            prefix = str(str(x)+'_').replace('.','p')
            directory = prefix+testID

            for QoI in QoIs:

                gp = gaussianProcess(trainPoints, devPoints, testPoints, yMax, PFDatabase, np.linspace(0.01,1.0,150))
                
                try:
                    os.mkdir('../GPRModels/'+directory+'_'+QoI)
                except:
                    print('Directory already exist')
                
                        
                with open('../GPRModels/'+directory+'_'+QoI+'.dat', 'w+') as out:
                    now = datetime.now()
                    out.write('\n'*10+'Gridsearch performed on ' + str(now.strftime("%d %m %Y, %H:%M:%S"))+ '\n'*10)
                    
                _ = joblib.Parallel(n_jobs=nCpu)(joblib.delayed(gp.gridsearch)(seed, features, directory, QoI)
                                        for seed in range(0,256))

    #############################################################

    elif mode == 'Inflow':
        
        print('here')

        for x in xModels:
            
            trainPoints = {'h':trainPairs[:,0],'r':trainPairs[:,1],'x':[x]}
            devPoints = {'h':devPairs[:,0],'r':devPairs[:,1],'x':[x]}
            testPoints = {'h':testPairs[:,0],'r':testPairs[:,1],'x':[x]}
            
            prefix = str(str(x)+'_').replace('.','p')
            directory = prefix+testID

            for QoI in QoIs:

                gp = gaussianProcess(trainPoints, devPoints, testPoints, yMax, PFDatabase, np.linspace(0.01,1.0,150))
                
                try:
                    os.mkdir('../GPRModels/'+directory+'_'+QoI)
                except:
                    print('Directory already exist')
                
                        
                with open('../GPRModels/'+directory+'_'+QoI+'.dat', 'w+') as out:
                    now = datetime.now()
                    out.write('\n'*10+'Gridsearch performed on ' + str(now.strftime("%d %m %Y, %H:%M:%S"))+ '\n'*10)
                    
                _ = joblib.Parallel(n_jobs=nCpu)(joblib.delayed(gp.gridsearch)(seed, features, directory, QoI)
                                        for seed in range(0,256))

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
                    
                    trainData = loadData([h], [x], [r], yMax, PFDatabase, 15.0, np.linspace(0.01,1.0,100))
                    
                    prefix = str(str(x)+'_').replace('.','p')
                    directory = prefix+testID
                    
                    model = '../GPRModels/'+directory+'_'+QoI+'.pkl'
                    
                    y_mean_train = gp.predict(model,trainData,features,QoI)
                    
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
                    
                    withheldData = loadData([h], [x], [r], yMax, PFDatabase, 15.0, np.linspace(0.01,1.0,100))
                    
                    prefix = str(str(x)+'_').replace('.','p')
                    directory = prefix+testID+'_'+QoI
                    
                    model = '../GPRModels/'+directory+'.pkl'
                    
                    y_mean_dev = gp.predict(model,withheldData,features,QoI)
                    
                    target.extend(withheldData[QoI].to_numpy()) 
                    prediction.extend(y_mean_dev['y_model'].to_numpy())
                    
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

            plt.legend()
            plt.savefig('../RegressionPlots/'+prefix+testID+'_'+setToPlot+'.png', bbox_inches='tight')
            plt.show()
            plt.close('all')
            
    ###############################
    
    elif mode == 'Write':

        allPairs = np.concatenate([trainPairs,devPairs,testPairs],axis=0)

        varList = ['x']+features+QoIs

        for x in xModels:
                    
            prefix = str(str(x)+'_').replace('.','p')
            
            DF = pd.DataFrame(columns=varList)
                            
            for h,r in allPairs:
                
                datapoint = loadData([h], [x], [r], yMax, PFDatabase, 15.0, np.linspace(0.01,1.0,150))[varList]
                datapoint['y'] = datapoint['y']*yMax
                datapoint['u'] = datapoint['u']*15.0
                DF = pd.concat([DF, datapoint[varList]], ignore_index=True)
                
            DF.rename(columns={col: col + ' LES' for col in QoIs}, inplace=True)

            for QoI in QoIs:
                
                trainPoints = {'h':trainPairs[:,0],'r':trainPairs[:,1],'x':[x]}
                devPoints = {'h':devPairs[:,0],'r':devPairs[:,1],'x':[x]}
                testPoints = {'h':testPairs[:,0],'r':testPairs[:,1],'x':[x]}
                
                gp = gaussianProcess(trainPoints, devPoints, testPoints, yMax, PFDatabase, np.linspace(0.01,1.0,150))
                
                DF_instance = pd.DataFrame(columns=['x']+features)
                predictions = []
                            
                for h,r in allPairs:
                    
                    datapoint = loadData([h], [x], [r], yMax, PFDatabase, 15.0, np.linspace(0.01,1.0,150))[varList]
                    directory = prefix+testID+'_'+QoI
                    
                    model = '../GPRModels/'+directory+'.pkl'
                    
                    y_GPR = gp.predict(model,datapoint,features,QoI)
                    
                    if QoI == 'u':
                        predictions = predictions + (y_GPR['y_model']*15.0).to_list()
                    else:
                        predictions = predictions + y_GPR['y_model'].to_list()
                
                DF[QoI+' GPR'] = predictions
                        
            DF.to_csv('Predictions/'+prefix+testID+'.csv',index=False)
                
                
                
                
                
                
                