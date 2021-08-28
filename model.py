from dataManager import *
import time

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler, StandardScaler
#import statsmodels.api as sm
from sklearn.metrics import mean_squared_error as mse
from sklearn.ensemble import GradientBoostingRegressor


class ModelManager(metaclass=SingletonMeta):
    def __init__(self):
        sales_ref_month2=DataManager().sales_ref_month_sin_ventas_mayores()
        num_var=['AREA','ALTO','DESCUENTO(%)','PRECIO','CANTIDAD',]
        cat_var=['MES','Factor covid','PUESTOS','COLOR_POS','CATEGORIA','SUBCATEGORIA_POS','VIGENCIA','ORIGEN','ESTILO','MATERIAL_POS','ACABADO','TIENDA']
        y=sales_ref_month2['CANTIDAD']
        X_num=sales_ref_month2[num_var[:-1]].astype('float')
        X_cat=sales_ref_month2[cat_var].astype('category')
        X_cat_dummies=pd.get_dummies(X_cat)
        scaler=MinMaxScaler()
        X_num_norm= scaler.fit_transform(X_num)
        X=np.append(X_num_norm,X_cat_dummies,axis=1)

        #split data till januar 2021
        index=sales_ref_month2[(sales_ref_month2.ANIO==2021)].index[0]
        X_train=X[:index-1]
        y_train=y[:index-1]
        X_test=X[index:]
        y_test=y[index:]

        ###########################


        #param_dist = {'n_estimators':[30, 40, 100, 200, 300],'learning_rate':[0.01, 0.05, 0.1, 0.3, 0.4, 1], 'max_depth': [2,4,6,8,10]}

        #self.grid_clf_br = GridSearchCV(GradientBoostingRegressor(), param_grid = param_dist,cv=3,n_jobs=4,scoring='neg_mean_squared_error')
        #self.grid_clf_br.fit(X_train, y_train)
        #best_params afeter this fit are {'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200}, the model was save in a file.
        #best={'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200}
        self.br=GradientBoostingRegressor(**{'learning_rate': 0.1, 'max_depth': 2, 'n_estimators': 300})
        #self.br=GradientBoostingRegressor(**best)

        self.br.fit(X_train,y_train)
        #print(mse(self.br.predict(X_test),y_test))
        y_predicted2=self.br.predict(X_test)
        ####################
        sales_train=sales_ref_month2[:index-1]
        sales_test=sales_ref_month2[index:]
        sales_train['predicted']=grid_clf_br.predict(X_train)
        sales_test['predicted']=grid_clf_br.predict(X_test)
        sales_test['fecha']= pd.to_datetime(sales_test['ANIO'].astype(str)+'/'+sales_test['MES'].astype(str))#,format="%Y/%M")
        sales_train['fecha']= pd.to_datetime(sales_train['ANIO'].astype(str)+'/'+sales_train['MES'].astype(str))#,format="%Y/%M")

        joint=pd.concat([sales_train,sales_test],axis=0)



        return mse(self.br.predict(X_test),y_test)

#ModelManager()




#############################




