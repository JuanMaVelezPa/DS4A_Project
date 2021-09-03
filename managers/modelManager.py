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
    def __init__(self):

        loaded_model_file = glob.glob("assets/model/model.pkl")
        loaded_model_data_file=glob.glob('assets/model/model_data.txt')
        
        if(len(loaded_model_file) == 0):
            print('Inició')
            self.__select_data(5) #5 only for 2 and 3 split data and predict 3 always.
            self.__split_data(3)
            
            print('Entrenando modelo')
            start = time.process_time()
            self.__train_model(3)
            #choose 1 for GB, 2 for statsmodel LR, 3 for Lasso Model, 4 for Ridge Model
            print('Se demora entrenando; ' + str((time.process_time() - start)/60))
            print('Modelo entrenado')
            
            self.__predict_data(3)
            print('Datos predecidos')

            print('Guardando datos')
            self.__save_data()
            
            print('Guardando modelo')
            self.__save_model()
            
            print('Modelo y datos persistidos')

        elif(len(loaded_model_data_file) == 0):
            self.__select_data(5)
            self.__split_data(3)
            
            self.model = joblib.load('assets/model/model.pkl')
            print('Modelo cargado')
            
            self.__predict_data(3)
            print('Datos predecidos')

            self.__save_data()
            print('Datos guardados')

        else:
            print('cargando datos')
            with open('assets/model/model_data.txt', 'r') as file:
                saved_data = json.loads(file.read())
                file.close()
                
                self.index = saved_data['index']
                self.date_index = saved_data['date_index']
                self.date_before = saved_data['date_before']
                self.date_after = saved_data['date_after']
                self.predicted_join = saved_data['df_predicted']
               
            self.model = joblib.load('assets/model/model.pkl')
            print('Todo Cargó')




    def __select_data(self,data_id):
        if(data_id == 1):
            self.data = DataManager().sales_ref_month_sin_ventas_mayores()
        elif(data_id == 2):
            self.data = DataManager().sales_accounting_zeroes()
        elif(data_id == 3):
            self.data = DataManager().sales_accounting_stores()
        elif(data_id == 4):
            self.data = DataManager().all_incorporated()
        elif(data_id == 5):
            self.data = DataManager().all_incorporated_lag() #ONLY FOR USE IN SPLIT MODE 2 and 3
    def __split_data(self,mode_id):
        if mode_id==1:
            self.scaler = MinMaxScaler()
            self.num_var=['PRECIO','AREA','ALTO','DESCUENTO(%)','CANTIDAD']
            x_num=self.data[self.num_var[:-1]].astype('float')
            x_num_norm = self.scaler.fit_transform(x_num)

            self.cat_var=[
                'MES',
                'TIENDA', 
                'PUESTOS', 
                'COLOR_POS', 'SUBCATEGORIA_POS', 'MATERIAL_POS',
                #'SUBCATEGORIA','MATERIAL','COLOR',
                'F_COVID' , 'ACABADO', 'CATEGORIA', 'ORIGEN'
                #quitamos anio, vigencia y estilo. validado: error casi no cambia y en el eda se demuestra
            ]
            x_cat=self.data[self.cat_var].astype('category')
            self.dummies = OneHotEncoder()
            self.dummies.fit(x_cat)
            x_cat_dummies=self.dummies.transform(x_cat).toarray()

            self.y = self.data['CANTIDAD']

            self.x = np.append(x_num_norm,x_cat_dummies,axis=1)
            
            #split data till januar 2021 and future
            self.index = self.data[(self.data.ANIO==2021)].index[0]
            self.max_index=self.data.tail(1).index[0]# from data, future begins here
            
            self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
            self.date_before=self.data.loc[self.index-1]['DATE']
            self.date_after=self.data.loc[self.index+1]['DATE']
            self.last_date_known=self.data.tail(1)['DATE'] #future begins here
            
            self.x_train = self.x[:self.index]
            self.y_train = self.y[:self.index]
            self.x_test = self.x[self.index:]
            self.y_test = self.y[self.index:]

            #incorporate data future
            data_future=DataManager().data_forecasting_2021()
            x_num_f=data_future[self.num_var[:-1]].astype('float')
            x_num_norm_f = self.scaler.transform(x_num_f)
            x_cat_f=data_future[self.cat_var].astype('category')
            x_cat_f_dummies=self.dummies.transform(x_cat_f).toarray()
            self.x_f = np.append(x_num_norm_f,x_cat_f_dummies,axis=1)


        ## Now these splits are developed for the data with laggy variables
        if mode_id==2: #for lagy CANTIDAD
            self.scaler = MinMaxScaler()
            
            self.num_var=['AREA','ALTO','DESCUENTO(%)','PRECIO']
            for i in range(1,13):
                self.num_var.append('CANTIDAD_{}'.format(i))
            self.num_var.append('CANTIDAD')
            x_num=self.data[self.num_var[:-1]].astype('float')
            x_num_norm = self.scaler.fit_transform(x_num)

            self.cat_var=[ 'MES','TIENDA', 'PUESTOS', 'COLOR_POS', 'SUBCATEGORIA_POS', 'F_COVID' ,
                        'MATERIAL_POS','ACABADO','CATEGORIA','ORIGEN'
                        #quitamos anio, vigencia y estilo-validado errro casi no cambia
                    ]
            x_cat=self.data[self.cat_var].astype('category')
            self.dummies = OneHotEncoder()
            self.dummies.fit(x_cat)
            x_cat_dummies=self.dummies.transform(x_cat).toarray()
            self.x = np.append(x_num_norm,x_cat_dummies,axis=1)
            self.y = self.data['CANTIDAD']
            
            self.index = self.data[(self.data.ANIO==2021)].index[0]
            self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
            self.date_before=self.data.iloc[self.index-1]['DATE']
            self.date_after=self.data.iloc[self.index+1]['DATE']

            self.x_train = self.x[:self.index]
            self.y_train = self.y[:self.index]
            self.x_test = self.x[self.index:]
            self.y_test = self.y[self.index:]

        if mode_id==3: #for laggy DIFF
            
            self.scaler = MinMaxScaler()
            self.num_var=['AREA','ALTO','DESCUENTO(%)','PRECIO']
            for i in range(1,12):
                self.num_var.append('DIFF_{}'.format(i))
            self.num_var.append('CANTIDAD')
            x_num=self.data[self.num_var[:-1]].astype('float')
            x_num_norm = self.scaler.fit_transform(x_num)

            self.cat_var=[ 'MES','TIENDA', 'PUESTOS', 'COLOR_POS', 'SUBCATEGORIA_POS', 'F_COVID' ,
                    'MATERIAL_POS','ACABADO','CATEGORIA','ORIGEN'
                    #quitamos anio, vigencia y estilo-validado errro casi no cambia
                ]
            x_cat=self.data[self.cat_var].astype('category')
            self.dummies = OneHotEncoder()
            self.dummies.fit(x_cat)
            x_cat_dummies=self.dummies.transform(x_cat).toarray()
            self.x = np.append(x_num_norm,x_cat_dummies,axis=1)
            self.y = self.data['CANTIDAD']
            
            self.index = self.data[(self.data.ANIO==2021)].index[0]
            self.date_index=self.data[(self.data.ANIO==2021)]['DATE'].values[0]
            self.date_before=self.data.iloc[self.index-1]['DATE']
            self.date_after=self.data.iloc[self.index+1]['DATE']

            self.x_train = self.x[:self.index]
            self.y_train = self.y[:self.index]
            self.x_test = self.x[self.index:]
            self.y_test = self.y[self.index:]

            
        


                            
    def __train_model(self,model_id):
        if(model_id == 1):
            self.model = GradientBoostingRegressor(**{'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200}) #best option but requires time to optimize...
            self.model.fit(self.x_train,self.y_train)
            self.model_f = GradientBoostingRegressor(**{'learning_rate': 0.01, 'max_depth': 6, 'n_estimators': 200}) #best option but requires time to optimize...
            self.model_f.fit(self.x,self.y)
        elif(model_id == 2):
            self.model = sm.OLS(self.y_train, sm.add_constant(self.x_train,has_constant='add'))# exploits in test_ needs L1 or L2 reg
            self.model=self.model.fit()
            self.model_f =sm.OLS(self.y, sm.add_constant(self.x,has_constant='add'))
            self.model_f=self.model_f.fit()
        elif(model_id==3):
            self.model=GridSearchCV(Lasso(), param_grid={'alpha': np.logspace(-3, 3, 10)},scoring='neg_mean_squared_error') #is better for small datasets: use if split is set to 2 or 3
            self.model.fit(self.x_train,self.y_train)
            self.params=self.model.best_params_
            self.model_f=Lasso(**self.params)
            self.model_f.fit(self.x,self.y)
            #print(self.x.shape)
        elif(model_id==4):
            self.model=GridSearchCV(Ridge(), param_grid={'alpha': np.logspace(-3, 3, 10)},scoring='neg_mean_squared_error')# is better for larger data sets: use in split 1
            self.model.fit(self.x_train,self.y_train)
            self.params=self.model.best_params_
            self.model_f=Ridge(**self.params)
            self.model_f.fit(self.x,self.y)
    
    def __predict_data(self,predict_id):
        if(predict_id==1):
            self.predicted = self.model.predict(self.x)#.round()
            self.predicted_f=self.model_f.predict(self.x_f)#.round()
        elif(predict_id==2):
            self.predicted=self.model.predict(sm.add_constant(self.x,has_constant='add')) 
            self.predicted_f=self.model_f.predict(sm.add_constant(self.x_f,hast_constant='add'))

        elif(predict_id==3):
            self.predicted=self.model.predict(self.x)
            data_future_lag=DataManager().data_forecasting_2021_lag()
            meses=data_future_lag.MES.unique()
            for i in meses:
                #print(i)
                aux=data_future_lag[data_future_lag['MES']==i].copy()
                x_num_i=aux[self.num_var[:-1]].astype('float')
                x_num_norm_i = self.scaler.transform(x_num_i)
                x_cat_i=aux[self.cat_var].astype('category')
                x_cat_dummies_i=self.dummies.transform(x_cat_i).toarray()
                #print(x_num_norm_i.shape)
                #print(x_cat_dummies_i.shape)
                #print(np.isnan(x_num_norm_i).any())
                #print(np.isnan(x_cat_dummies_i).any())
                x=np.append(x_num_norm_i,x_cat_dummies_i,axis=1)
                aux=self.model_f.predict(x)
                for j in meses:
                    if j-i==0:
                        #print(aux.shape)
                        data_future_lag.loc[data_future_lag['MES']==j,'CANTIDAD']=aux
                    elif j-i>0:
                        data_future_lag.loc[data_future_lag['MES']==j,'CANTIDAD_{}'.format(j-i)]=aux 
                        data_future_lag.loc[data_future_lag['MES']==j,'DIFF_{}'.format(j-i)]=data_future_lag.loc[data_future_lag['MES']==j,'CANTIDAD_{}'.format(j-i)]-data_future_lag.loc[data_future_lag['MES']==j,'CANTIDAD_{}'.format(j-i+1)]
            self.predicted_f=data_future_lag['CANTIDAD']
        self.predicted_join=np.append(self.predicted,self.predicted_f,axis=0)

    def __save_data(self):
        to_save = {
            'index':self.index.item(),
            'date_index':self.date_index,
            'date_before':self.date_before,
            'date_after':self.date_after,
            'df_predicted':self.predicted_join.tolist()
        }

        with open('assets/model/model_data.txt', 'w') as outfile:
            json.dump(to_save, outfile)

    def __save_model(self):
        joblib.dump(self.model,'assets/model/model.pkl')

    def get_data(self):
        indexes = [self.index, self.date_index, self.date_before, self.date_after]
        return indexes, self.predicted_join