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

import time


class ModelManager(metaclass=SingletonMeta):
    def __init__(self):

        loaded_model_file = glob.glob("assets/model/model.pkl")
        loaded_model_data_file=glob.glob('assets/model/model_data.txt')
        if(len(loaded_model_file) == 0):
            print('Inició')
            self.__select_data__(3)
            self.__split_data__()
            print('Entrenando modelo')
            start = time.process_time()
            self.__model__(1)
            print('Se demora entrenando; ' + str((time.process_time() - start)/60))
            print('Modelo entrenado')
            self.__predicted_dataframe__()
            print('datos predecidos')

            to_save = {
                #'data':self.data.to_json(),
                'index':self.index.item(),
                'date_index':self.date_index,
                'date_before':self.date_before,
                'date_after':self.date_after,
                'df_predicted':self.data.to_json()
            }
            print('Guardando datos')
            with open('assets/model/model_data.txt', 'w') as outfile:
                json.dump(to_save, outfile)
            
            joblib.dump(self.br,'assets/model/model.pkl')
            print('Modelo y datos persistidos')

        elif(len(loaded_model_data_file) == 0):
            self.__select_data__(3)
            self.__split_data__()
            self.br = joblib.load('assets/model/model.pkl')
            print('El modelo cargó')
            self.__predicted_dataframe__()
            print('datos predecidos')

            to_save = {
                #'data':self.data.to_json(),
                'index':self.index.item(),
                'date_index':self.date_index,
                'date_before':self.date_before,
                'date_after':self.date_after,
                'df_predicted':self.data.to_json()
            }
            print('Guardando datos')
            with open('assets/model/model_data.txt', 'w') as outfile:
                json.dump(to_save, outfile)
            

        else:
            with open('assets/model/model_data.txt', 'r') as file:
                saved_data = json.loads(file.read())
                file.close()
                #self.data = pd.read_json(saved_data['data'])
                self.index = saved_data['index']
                self.date_index = saved_data['date_index']
                self.date_before = saved_data['date_before']
                self.date_after = saved_data['date_after']
                self.data=pd.read_json(saved_data['df_predicted'])
               
            self.br = joblib.load('assets/model/model.pkl')
            print('Todo Cargó')



    def __select_data__(self,data_id):
        if(data_id == 1):
            self.data = DataManager().sales_ref_month_sin_ventas_mayores()
        elif(data_id == 2):
            self.data = DataManager().sales_accounting_zeroes()
        elif(data_id == 3):
            self.data = DataManager().sales_accounting_stores()

    def __split_data__(self):
        num_var=['PRECIO','AREA','ALTO','DESCUENTO(%)','CANTIDAD']
        x_num=self.data[num_var[:-1]].astype('float')

        cat_var=[
            'MES',
            'TIENDA', 
            'PUESTOS', 'COLOR_POS', 'SUBCATEGORIA_POS', 'F_COVID' ,'MATERIAL_POS','ACABADO','CATEGORIA','ORIGEN'
            #quitamos anio, vigencia y estilo. validado: error casi no cambia y en el eda se demuestra
        ]
        x_cat=self.data[cat_var].astype('category')
        x_cat_dummies=pd.get_dummies(x_cat)

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
    
    def __predicted_dataframe__(self):
         self.data['PREDICTED'] = self.br.predict(np.concatenate([self.x_train,self.x_test],axis=0)).round()
        
    

    def get_data(self):
        indexes = [self.index, self.date_index, self.date_before, self.date_after]
        return indexes, self.data


