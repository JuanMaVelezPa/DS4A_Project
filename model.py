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
            self.__select_data__(1)
            self.__split_data__()
            
            print('Entrenando modelo')
            start = time.process_time()
            self.__train_model__(1)
            print('Se demora entrenando; ' + str((time.process_time() - start)/60))
            print('Modelo entrenado')
            
            self.__predict_data__()
            print('Datos predecidos')

            print('Guardando datos')
            self.__save_data__()
            
            print('Guardando modelo')
            self.__save_model__()
            
            print('Modelo y datos persistidos')

        elif(len(loaded_model_data_file) == 0):
            self.__select_data__(1)
            self.__split_data__()
            
            self.br = joblib.load('assets/model/model.pkl')
            print('Modelo cargado')
            
            self.__predict_data__()
            print('Datos predecidos')

            self.__save_data__()
            print('Datos guardados')

        else:
            with open('assets/model/model_data.txt', 'r') as file:
                saved_data = json.loads(file.read())
                file.close()
                
                self.index = saved_data['index']
                self.date_index = saved_data['date_index']
                self.date_before = saved_data['date_before']
                self.date_after = saved_data['date_after']
                self.predicted = saved_data['df_predicted']
               
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
        #incorporate data future
        num_var=['PRECIO','AREA','ALTO','DESCUENTO(%)','CANTIDAD']

        data_future=DataManager().data_forecasting_2021()

        df_concat=pd.concat([self.data.drop('CANTIDAD',axis=1),data_future]).reset_index(drop=True)
        self.max_index=self.data.tail(1).index[0]

        x_num=df_concat[num_var[:-1]].astype('float')


        cat_var=[
            'MES',
            'TIENDA', 
            'PUESTOS', 
            'COLOR_POS', 'SUBCATEGORIA_POS', 'MATERIAL_POS',
            #'SUBCATEGORIA','MATERIAL','COLOR',
            'F_COVID' , 'ACABADO', 'CATEGORIA', 'ORIGEN'
            #quitamos anio, vigencia y estilo. validado: error casi no cambia y en el eda se demuestra
        ]
        x_cat=df_concat[cat_var].astype('category')
        x_cat_dummies=pd.get_dummies(x_cat)

        y = self.data['CANTIDAD']

        scaler = MinMaxScaler()
        x_num_norm = scaler.fit_transform(x_num)
        x = np.append(x_num_norm,x_cat_dummies,axis=1)
        
        #split data till januar 2021 and future
        self.index = self.data[(self.data.ANIO==2021)].index[0]
        self.max_index=self.data.tail(1).index[0]# from data, future begins here
       
        self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
        self.date_before=self.data.loc[self.index-1]['DATE']
        self.date_after=self.data.loc[self.index+1]['DATE']
        self.last_date_known=self.data.tail(1)['DATE'] #future begins here
        

        self.x_train = x[:self.index]
        self.y_train = y[:self.index]
        self.x_test = x[self.index:self.max_index+1]
        self.y_test = y[self.index:]
        self.x_future=x[self.max_index+1:]

    def __train_model__(self,model_id):
        if(model_id == 1):
            self.br = GradientBoostingRegressor(**{'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200})
        elif(model_id == 2):
            self.br = None
        
        self.br.fit(self.x_train,self.y_train)
    
    def __predict_data__(self):
        self.predicted = self.br.predict(np.concatenate([self.x_train,self.x_test,self.x_future],axis=0)).round()
        
    def __save_data__(self):
        to_save = {
            'index':self.index.item(),
            'date_index':self.date_index,
            'date_before':self.date_before,
            'date_after':self.date_after,
            'df_predicted':self.predicted.tolist()
        }

        with open('assets/model/model_data.txt', 'w') as outfile:
            json.dump(to_save, outfile)

    def __save_model__(self):
        joblib.dump(self.br,'assets/model/model.pkl')

    def get_data(self):
        indexes = [self.index, self.date_index, self.date_before, self.date_after]
        return indexes, self.predicted