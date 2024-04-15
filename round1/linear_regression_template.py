#How to combine multiple files of csv with 8 lines of code
import pandas as pd
import numpy as np  

df=pd.read_csv("day1_simple_good.csv")

#the response
y=df.loc[:,"price"]
y=y.to_numpy()

#the features
X=df[["quantity"] ]
X=X.to_numpy()

n=10000
         
#get X-train,y-train,x-test,y-test

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state = 0)


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
D[:,1:nParam]=predictors.iloc[:,0:predictors.shape[1]]
D_pseudoinverse=np.linalg.pinv(D)
b=np.dot(D_pseudoinverse,y)

"""
Step 2: See the results on the test set; comparing R2, Slof_fit
"""
y_hat=b[0]
for i in range(1,nParam):
    y_hat+=b[i]*D[:,i]

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
Step 3: T-test to see the most important features and remove the 
"""