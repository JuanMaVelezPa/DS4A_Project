
import numpy as np
import pandas as pd

from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler, StandardScaler,OneHotEncoder 
from sklearn.metrics import mean_squared_error as mse
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Lasso, Ridge
import statsmodels.api as sm

from managers.dataManager import *

import joblib
import glob
import json
import time

class ModelManager(metaclass=SingletonMeta):
    def __init__(self,data_type=3,lag_type=2,is_auto=True,num=12,model_type=3,predict_type=2):

        loaded_model_file = glob.glob("assets/model/model.pkl")
        loaded_model_data_file=glob.glob('assets/model/model_data.txt')
        
        if(len(loaded_model_file) == 0):
            print('Inició')
            
            # __select_data(data_type) 
            # data_type = 1 for normal data, 2 for lagged data or 3 for automatic lagged future data
            self.__select_data(data_type,num)
            
            # __split_data(lag_type,is_auto) 
            # lag_type = 1 for CANTIDAD or 2 for DIFF
            # is_auto = True or False
            self.__split_data(lag_type,is_auto,num) 

            print('Entrenando modelo')
            start = time.process_time()
            
            # __train_model(model_type)
            # model_type = 1 for GB, 2 for statsmodel LR, 3 for Lasso Model or 4 for Ridge Model
            self.__train_model(model_type)
            print('Se demora entrenando; ' + str((time.process_time() - start)/60))
            print('Modelo entrenado')
            
            self.__predict_data(predict_type)
            print('Datos predecidos')

            print('Guardando datos')
            self.__save_data()
            
            print('Guardando modelo')
            self.__save_model()
            
            print('Modelo y datos persistidos')

        elif(len(loaded_model_data_file) == 0):
            self.__select_data(3)
            self.__split_data(2,True)
            
            self.model = joblib.load('assets/model/model.pkl')
            print('Modelo cargado')
            
            self.__predict_data(2)
            print('Datos predecidos')

            self.__save_data()
            print('Datos guardados')

        else:
            print('Cargando datos')
            with open('assets/model/model_data.txt', 'r') as file:
                saved_data = json.loads(file.read())
                file.close()
                
                self.index = saved_data['index']
                self.date_index = saved_data['date_index']
                self.date_before = saved_data['date_before']
                self.date_after = saved_data['date_after']
                self.predicted = saved_data['predicted']
               
            self.model = joblib.load('assets/model/model.pkl')
            print('Todo Cargó')

    def __select_data(self,data_id,num):
        if(data_id == 1):
            self.data = DataManager().all_data()
        elif(data_id == 2):
            self.data = DataManager().all_data_lag(num)
        elif(data_id == 3):
            self.data, self.index = DataManager().all_data_future_lag(num)
    
    def __split_data(self,lag_type,is_auto,num):
        self.num_var=['PRECIO','AREA','ALTO','DESCUENTO(%)']
        if lag_type == 1: # CANTIDAD
            for i in range(1,num):
                self.num_var.append('CANTIDAD_{}'.format(i))
        if lag_type == 2: # DIFF
            for i in range(1,num):
                self.num_var.append('DIFF_{}'.format(i))
        self.num_var.append('CANTIDAD')
        
        self.scaler = MinMaxScaler()
        x_num=self.data[self.num_var[:-1]].astype('float')
        x_num_norm = self.scaler.fit_transform(x_num)
        
        self.cat_var=[
            'MES','TIENDA','PUESTOS','COLOR_POS', 'SUBCATEGORIA_POS',
            'MATERIAL_POS','F_COVID','ACABADO','CATEGORIA','ORIGEN'
        ]
        x_cat=self.data[self.cat_var].astype('category')
        self.dummies = OneHotEncoder()
        self.dummies.fit(x_cat)
        x_cat_dummies=self.dummies.transform(x_cat).toarray()
        
        self.x = np.append(x_num_norm,x_cat_dummies,axis=1)
        self.y = self.data['CANTIDAD']
        
        if(not is_auto):
            self.index = self.data[(self.data.ANIO==2021)].index[0]
            self.date_index = self.data[(self.data.ANIO==2021)]['DATE'].values[0]
            self.date_before = self.data.iloc[self.index-1]['DATE']
            self.date_after = self.data.iloc[self.index+1]['DATE']
        else:
            self.date_index = self.data.iloc[self.index].DATE
            self.date_before = self.data.iloc[self.index-1].DATE
            self.date_after = self.data.iloc[self.index+1].DATE
        
        self.x_past = self.x[:-self.index]
        self.x_train = self.x_past[:-int(len(self.x_past)*0.25)]
        self.x_fut = self.x[-self.index:]

        self.y_past = self.y[:-self.index]
        self.y_train = self.y_past[:-int(len(self.y_past)*0.25)]
            

    def __train_model(self,model_id):
        if(model_id == 1):
            self.model = GradientBoostingRegressor(**{'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200}) #best option but requires time to optimize...
            self.model.fit(self.x_train,self.y_train)
            self.model_f = GradientBoostingRegressor(**{'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200}) #best option but requires time to optimize...
            self.model_f.fit(self.x_past,self.y_past)
        elif(model_id == 2):
            self.model = sm.OLS(self.y_train, sm.add_constant(self.x_train,has_constant='add'))# exploits in test_ needs L1 or L2 reg
            self.model=self.model.fit()
            self.model_f =sm.OLS(self.y_past, sm.add_constant(self.x_past,has_constant='add'))
            self.model_f=self.model_f.fit()
        elif(model_id==3):
            self.model=GridSearchCV(Lasso(), param_grid={'alpha': np.logspace(-3, 3, 10)},scoring='neg_mean_squared_error') #is better for small datasets: use if split is set to 2 or 3
            self.model.fit(self.x_train,self.y_train)
            self.params = self.model.best_params_
            self.model_f = Lasso(**self.params)
            self.model_f.fit(self.x_past,self.y_past)
        elif(model_id==4):
            self.model = GridSearchCV(Ridge(), param_grid={'alpha': np.logspace(-3, 3, 10)},scoring='neg_mean_squared_error')# is better for larger data sets: use in split 1
            self.model.fit(self.x_train,self.y_train)
            self.params = self.model.best_params_
            self.model_f = Ridge(**self.params)
            self.model_f.fit(self.x_past,self.y_past)
    
    def __predict_data(self,predict_id=2):
        if(predict_id == 1):
            self.pred_past = self.model.predict(self.x_past)

            fut = self.data[-self.index:]
            meses = fut.MES.unique()

            for i in meses:
                mes = fut[fut['MES']==i].copy()
                
                x_num = mes[self.num_var[:-1]].astype('float')
                x_num_norm = self.scaler.transform(x_num)
                
                x_cat = mes[self.cat_var].astype('category')
                x_cat_dummies = self.dummies.transform(x_cat).toarray()
                
                x = np.append(x_num_norm,x_cat_dummies,axis=1)

                pred = self.model_f.predict(x)

                for j in meses:
                    if j-i == 0:
                        fut.loc[fut['MES']==j,'CANTIDAD'] = pred
                    elif j-i > 0:
                        fut.loc[fut['MES']==j,'CANTIDAD_{}'.format(j-i)] = pred
                        fut.loc[fut['MES']==j,'DIFF_{}'.format(j-i)] = fut.loc[fut['MES']==j,'CANTIDAD_{}'.format(j-i)] - fut.loc[fut['MES']==j,'CANTIDAD_{}'.format(j-i+1)]

            self.pred_fut = fut['CANTIDAD']
        elif(predict_id == 2):
            self.pred_past = self.model.predict(self.x_past)
            self.pred_fut = self.model_f.predict(self.x_fut)
        self.predicted = np.append(self.pred_past,self.pred_fut,axis=0)

    def __save_data(self):
        to_save = {
            'index':self.index,
            'date_index':self.date_index,
            'date_before':self.date_before,
            'date_after':self.date_after,
            'predicted':self.predicted.tolist()
        }

        with open('assets/model/model_data.txt', 'w') as outfile:
            json.dump(to_save, outfile)

    def __save_model(self):
        joblib.dump(self.model,'assets/model/model.pkl')

    def get_data(self):
        indexes = [self.index, self.date_index, self.date_before, self.date_after]
        return indexes, self.predicted