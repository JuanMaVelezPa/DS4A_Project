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
            data = DataManager().sales_ref_month_sin_ventas_mayores()

            num_var=['AREA','ALTO','DESCUENTO(%)','PRECIO','CANTIDAD',]
            X_num=data[num_var[:-1]].astype('float')
            
            cat_var=['MES','F_COVID','PUESTOS','COLOR_POS','CATEGORIA','SUBCATEGORIA_POS','VIGENCIA','ORIGEN','ESTILO','MATERIAL_POS','ACABADO','TIENDA']
            X_cat=data[cat_var].astype('category')
            X_cat_dummies=pd.get_dummies(X_cat)
            
            y = data['CANTIDAD']
            
            scaler = MinMaxScaler()
            X_num_norm = scaler.fit_transform(X_num)
            X = np.append(X_num_norm,X_cat_dummies,axis=1)

            #split data till januar 2021
            self.index = data[(data.ANIO==2021)].index[0]
            
            self.X_train = X[:self.index-1]
            self.y_train = y[:self.index-1]
            self.X_test = X[self.index-1:]
            self.y_test = y[self.index-1:]

            to_save = {
                'index':self.index.item(),
                'x_train':self.X_train.tolist(),
                'y_train':self.y_train.tolist(),
                'x_test':self.X_test.tolist(),
                'y_test':self.y_test.tolist()
            }
            with open('assets/model/model_data.txt', 'w') as outfile:
                json.dump(to_save, outfile)

            ## Change from here
            self.br = GradientBoostingRegressor(**{'learning_rate': 0.1, 'max_depth': 2, 'n_estimators': 300})
            self.br.fit(self.X_train,self.y_train)
            ## Change to here

            joblib.dump(self.br,'assets/model/model.pkl')
            print('Persistió')
        else:
            with open('assets/model/model_data.txt', 'r') as file:
                data = json.loads(file.read())
                file.close()
                self.index = data['index']
                self.X_train = data['x_train']
                self.y_train = data['y_train']
                self.X_test = data['x_test']
                self.y_test = data['y_test']
               
            self.br = joblib.load('assets/model/model.pkl')
            print('Cargó')

        self.mse = mse(self.br.predict(self.X_test),self.y_test)

    def get_data(self):
        return self.index, self.X_train, self.y_train, self.X_test, self.y_test 



