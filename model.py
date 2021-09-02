import numpy as np
import pandas as pd

from dataManager import *

from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error as mse
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm


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
            self.__select_data__(4)
            self.__split_data__(1)
            
            print('Entrenando modelo')
            start = time.process_time()
            self.__train_model__(2)
            print('Se demora entrenando; ' + str((time.process_time() - start)/60))
            print('Modelo entrenado')
            
            self.__predict_data__(2)
            print('Datos predecidos')

            print('Guardando datos')
            self.__save_data__()
            
            print('Guardando modelo')
            self.__save_model__()
            
            print('Modelo y datos persistidos')

        elif(len(loaded_model_data_file) == 0):
            self.__select_data__(4)
            self.__split_data__(1)
            
            self.model = joblib.load('assets/model/model.pkl')
            print('Modelo cargado')
            
            self.__predict_data__(2)
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
               
            self.model = joblib.load('assets/model/model.pkl')
            print('Todo Cargó')




    def __select_data__(self,data_id):
        if(data_id == 1):
            self.data = DataManager().sales_ref_month_sin_ventas_mayores()
        elif(data_id == 2):
            self.data = DataManager().sales_accounting_zeroes()
        elif(data_id == 3):
            self.data = DataManager().sales_accounting_stores()
        elif(data_id == 4):
            self.data = DataManager().all_incorporated()
        elif(data_id == 5):
            self.data = DataManager().all_incorporated_lag() #ONLY FOR USE IN SPLIT MODE 2

    def __split_data__(self,mode_id):
        if mode_id==1:

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
            self.x = np.append(x_num_norm,x_cat_dummies,axis=1)
            
            #split data till januar 2021 and future
            self.index = self.data[(self.data.ANIO==2021)].index[0]
            self.max_index=self.data.tail(1).index[0]# from data, future begins here
            
            self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
            self.date_before=self.data.loc[self.index-1]['DATE']
            self.date_after=self.data.loc[self.index+1]['DATE']
            self.last_date_known=self.data.tail(1)['DATE'] #future begins here
            

            self.x_train = self.x[:self.index]
            self.y_train = y[:self.index]
            self.x_test = self.x[self.index:self.max_index+1]
            self.y_test = y[self.index:]
            self.x_future=self.x[self.max_index+1:]
            


        if mode_id==2:

        
            num_var=['AREA','ALTO','DESCUENTO(%)','PRECIO']
            for i in range(1,13):
                num_var.append('CANTIDAD_{}'.format(i))
            num_var.append('CANTIDAD')
            x_num=self.data[num_var[:-1]].astype('float')


            cat_var=[ 'MES','TIENDA', 'PUESTOS', 'COLOR_POS', 'SUBCATEGORIA_POS', 'F_COVID' ,
                        'MATERIAL_POS','ACABADO','CATEGORIA','ORIGEN'
                        #quitamos anio, vigencia y estilo-validado errro casi no cambia
                    ]
            x_cat=self.data[cat_var].astype('category')
            x_cat_dummies=pd.get_dummies(x_cat)

            y = self.data['CANTIDAD']

            scaler = MinMaxScaler()
            x_num_norm = scaler.fit_transform(x_num)
            self.x = np.append(x_num_norm,x_cat_dummies,axis=1)

            #split data till januar 2021

            self.index = self.data[(self.data.ANIO==2021)].index[0]
            self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
            self.date_before=self.data.iloc[self.index-1]['DATE']
            self.date_after=self.data.iloc[self.index+1]['DATE']

            self.x_train = self.x[:self.index]
            self.y_train = y[:self.index]
            self.x_test = self.x[self.index:]
            self.y_test = y[self.index:]

            print(self.x_train.shape)
            print(self.y_train.shape)
            print(self.x_test.shape)
            print(self.y_test.shape)
            




       
    def __train_model__(self,model_id):
        if(model_id == 1):
            self.model = GradientBoostingRegressor(**{'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200})
            self.model.fit(self.x_train,self.y_train)
        elif(model_id == 2):
            self.model = sm.OLS(self.y_train, sm.add_constant(self.x_train,has_constant='add'))
            self.model=self.model.fit()
    
    def __predict_data__(self,predict_id):
        if(predict_id==1):
            self.predicted = self.model.predict(self.x).round()
        elif(predict_id==2):
            self.predicted=self.model.predict(sm.add_constant(self.x,has_constant='add')) #es similar a L2 de Ridge de sklearn, o tal vez algo pasa con sklearn.. porque si hago l2 con alpha peque;o coincide.. raro


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
        joblib.dump(self.model,'assets/model/model.pkl')

    def get_data(self):
        indexes = [self.index, self.date_index, self.date_before, self.date_after]
        return indexes, self.predicted