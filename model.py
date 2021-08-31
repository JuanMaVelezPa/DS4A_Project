import numpy as np
import pandas as pd

from dataManager import *

from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error as mse
from sklearn.ensemble import GradientBoostingRegressor

import joblib
import glob
import json

class ModelManager(metaclass=SingletonMeta):
    def __init__(self):

        loaded_model_file = glob.glob("assets/model/model.pkl")
        if(len(loaded_model_file) == 0):
            self.__select_data__(2)
            self.__split_data__()
            self.__model__(1)

            to_save = {
                'data':self.data.to_json(),
                'index':self.index.item(),
                'date_index':self.date_index,
                'date_before':self.date_before,
                'date_after':self.date_after,
                'x_train':self.x_train.tolist(),
                'y_train':self.y_train.tolist(),
                'x_test':self.x_test.tolist(),
                'y_test':self.y_test.tolist()
            }
            with open('assets/model/model_data.txt', 'w') as outfile:
                json.dump(to_save, outfile)
            
            joblib.dump(self.br,'assets/model/model.pkl')
            print('Persistió')
        else:
            with open('assets/model/model_data.txt', 'r') as file:
                saved_data = json.loads(file.read())
                file.close()
                self.data = pd.read_json(saved_data['data'])
                self.index = saved_data['index']
                self.date_index = saved_data['date_index']
                self.date_before = saved_data['date_before']
                self.date_after = saved_data['date_after']
                self.x_train = saved_data['x_train']
                self.y_train = saved_data['y_train']
                self.x_test = saved_data['x_test']
                self.y_test = saved_data['y_test']
               
            self.br = joblib.load('assets/model/model.pkl')
            print('Cargó')

        self.mse = mse(self.br.predict(self.x_test),self.y_test)

    def __select_data__(self,data_id):
        if(data_id == 1):
            self.data = DataManager().sales_ref_month_sin_ventas_mayores()
        elif(data_id == 2):
            self.data = DataManager().sales_accounting_zeroes()

    def __split_data__(self):
        num_var = ['AREA','ALTO','DESCUENTO(%)','PRECIO','CANTIDAD']
        x_num = self.data[num_var[:-1]].astype('float')
        
        cat_var = ['ANIO', 'MES', 'PUESTOS', 'COLOR_POS', 'SUBCATEGORIA_POS', 'ESTILO', 'F_COVID']
        x_cat = self.data[cat_var].astype('category')
        x_cat_dummies = pd.get_dummies(x_cat)
        
        y = self.data['CANTIDAD']
        
        scaler = MinMaxScaler()
        x_num_norm = scaler.fit_transform(x_num)
        x = np.append(x_num_norm,x_cat_dummies,axis=1)

        #split data till januar 2021
        self.index = self.data[(self.data.ANIO==2021)].index[0]
       
        self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
        self.date_before=self.data.loc[self.index-1]['DATE']
        self.date_after=self.data.loc[self.index+1]['DATE']
        
        self.x_train = x[:self.index]
        self.y_train = y[:self.index]
        self.x_test = x[self.index:]
        self.y_test = y[self.index:]

    def __model__(self,model_id):
        if(model_id == 1):
            self.br = GradientBoostingRegressor(**{'learning_rate': 0.1, 'max_depth': 2, 'n_estimators': 300})
        elif(model_id == 2):
            self.br = None
        
        self.br.fit(self.x_train,self.y_train)

    def get_data(self):
        return self.index, self.date_index, self.date_before,self.date_after, self.x_train, self.y_train, self.x_test, self.y_test, self.data



