import os
import pandas as pd
import numpy as np  
import statistics as stats

os.chdir("/Users/michellenguyen/Documents/round2_data")
df1=pd.read_csv("prices_round_2_day_-1.csv")
df2=pd.read_csv("prices_round_2_day_0.csv")
df3=pd.read_csv("prices_round_2_day_1.csv")

df = pd.concat([df1,df2,df3], axis=0)
y=df.iloc[:,1]
y=y.to_numpy()
predictors_to_choose=['TRANSPORT_FEES', 
                      'EXPORT_TARIFF',
                      'IMPORT_TARIFF', 
                      'SUNLIGHT', 
                      'HUMIDITY']
X=df[predictors_to_choose]
X=X.to_numpy()
      

np.random.seed(3)  
taken_index= np.random.choice(X.shape[0], size=(18000,), replace=False)
taken_index=list(taken_index)
X_train=X[taken_index,:]
y_train=y[taken_index]

other_index=[]
for i in range(30003):
    if (i in taken_index)==False:
        other_index.append(i)
X_test=X[other_index,:]
y_test=y[other_index] 

"""
Step 1: Find the model on the training set
"""
response= y_train
predictors=X_train

nExpt = predictors.shape[0] #eg number of data points
no_predictors=predictors.shape[1]
nParam = no_predictors+1 #number of parameters

y = y_train
D = np.zeros((nExpt,nParam))
D[:,0]=1
D[:,1:nParam]=predictors[:,0:predictors.shape[1]]
D_pseudoinverse=np.linalg.pinv(D)
b=np.dot(D_pseudoinverse,y)

"""
Step 2: See the results on the train set; comparing R2, Slof_fit
"""
y_hat=b[0]
for i in range(1,nParam):
    y_hat+=b[i]*D[:,i]

print("values of test on the train set are:")
#R2 and Slof_fit
S_resid=np.sum((y-y_hat)**2)
N=nExpt
P=nParam
print('S_resid is',S_resid)

#S_lof=S_resid-S_rep
R=0
S_lof=S_resid
dof=N-P-R
print('S_lof/d is',S_lof/dof)

# Calculating R2 Score
mean_y=np.mean(y)
ss_tot = 0
ss_res = 0
ss_tot= np.sum((y- mean_y) ** 2)
ss_res= np.sum((y- y_hat) ** 2)
r2 = 1 - (ss_res/ss_tot)
print("R2 Score",r2)
print('\n')

"""
Step 3: Fine tune the parameters
"""

from scipy import stats

#T-TESTS AND RAZOR

S_resid=np.sum((y-y_hat)**2)

nExpt = X_train.shape[0] #eg number of data points
no_predictors=X_train.shape[1]
nParam = no_predictors+1 #number of parameters

N=nExpt
P=nParam
s_2=S_resid/(N-P)

D_coded=np.zeros((nExpt,nParam))
D_coded[:,0]=1

#Standardise the value
for i in range(1,nParam):
    a1=np.max(D[:,i])
    b1=np.min(D[:,i])
    D_coded[:,i]=(D[:,i]-((a1+b1)/2))/((a1-b1)/2)

D_transpose=np.transpose(D_coded)
D_2=np.linalg.inv(np.dot(D_transpose,D_coded))
vb_2=np.diagonal(D_2) 
t=b/np.sqrt(s_2*vb_2) #the t-values of each predictor

dof=N-P #dofis N-P
qt=90/100 
q1t=1-2*(1-qt) #q1t is the confidence level of the 1-tailed testm, qt is the level of the 2-tailed test
t_crit_q=stats.t.ppf(qt,dof)
RH=(np.abs(t)>t_crit_q) #RH is the array of true/false value of each predictor

"""
Step 4: See the results on the test set; comparing R2, Slof_fit 
"""

response_test= y_test
predictors_test=X_test
nExpt_test = predictors_test.shape[0] #eg number of data points
no_predictors_test=predictors_test.shape[1]
nParam_test = no_predictors_test+1 #number of parameters
D_test = np.zeros((nExpt_test,nParam_test))
D_test[:,0]=1
D_test[:,1:nParam_test]=predictors_test[:,0:predictors_test.shape[1]]

y_hat_test=b[0]
for i in range(1,nParam_test):
    y_hat_test+=b[i]*D_test[:,i]

print("values of test on the test set are:")
#R2 and Slof_fit
S_resid=np.sum((y_test-y_hat_test)**2)
N=nExpt_test
P=nParam_test
print('S_resid is',S_resid)

#S_lof=S_resid-S_rep
R=0
S_lof=S_resid
dof=N-P-R
print('S_lof/d is',S_lof/dof)

# Calculating R2 Score
mean_y=np.mean(y_test)
ss_tot = 0
ss_res = 0
ss_tot= np.sum((y_test- mean_y) ** 2)
ss_res= np.sum((y_test- y_hat_test) ** 2)
r2 = 1 - (ss_res/ss_tot)
print("R2 Score",r2)
print('\n')


