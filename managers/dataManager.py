import pandas as pd
import numpy as np
class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataManager(metaclass=SingletonMeta):

    def __clean_products(self,products):
        products.columns = [column.upper() for column in products.columns]
        products.columns = [column.lstrip('001-') for column in products.columns]
        products.columns = [column.replace('.', '') for column in products.columns]
        products.columns = [column.replace(' ', '_') for column in products.columns]
        products.columns = [column.replace('_EXHIBIDO', '') for column in products.columns]
        products.columns = [column.replace('_UNIFICADA', '') for column in products.columns]
        products = products.rename(columns={
            'DESC_ITEM':'DESC_LARGA',
            'DESC_EXT_1_DETALLE':'DETALLE_1',
            'DESC_EXT_2_DETALLE':'DETALLE_2',
            'DESC_TIPO_INVENTARIO':'TIPO_INVENTARIO',
            'DEPARTAMENTO':'CATEGORIA',
            'MATERIAL_PPAL':'MATERIAL',
            'PUESTOS':'PUESTOS_STR',
            'NUM_PUESTOS':'PUESTOS',
            'REF_COMBINADA':'REF',
            'COLOR_DEF':'COLOR',
            })

        regex = '^([A-Z0-9]+\s\-\s)+'
        products.SUBCATEGORIA = products.SUBCATEGORIA.str.replace(regex,'',regex=True)
        products.ORIGEN = products.ORIGEN.str.replace(regex,'',regex=True)
        products.CATEGORIA = products.CATEGORIA.str.replace(regex,'',regex=True)
        products.ESTILO = products.ESTILO.str.replace(regex,'',regex=True)
        products.VIGENCIA = products.VIGENCIA.str.replace(regex,'',regex=True)
        products.MATERIAL = products.MATERIAL.str.replace(regex,'',regex=True).str.upper()
        products.ACABADO = products.ACABADO.str.upper().replace('SUPERFICIES MATE','MATE')
        products.DETALLE_1.fillna('N/A',inplace=True)
        products.DETALLE_2.fillna('N/A',inplace=True)
        products['PUESTOS'] = products.PUESTOS_STR.str.slice(stop=1).replace({'N':0,'M':7}).astype(int).replace({0:np.nan})
        products['AREA'] = products.ANCHO * products.FONDO
        products = products[['ITEM','REF','DESCRIPCION','CATEGORIA','SUBCATEGORIA','VIGENCIA','ORIGEN', 
            'ESTILO','MATERIAL','ACABADO','PUESTOS','COLOR','AREA','ANCHO','ALTO','FONDO','DESC_LARGA']]
        return products

    def __clean_sales(self,sales):
        sales.columns = [column.upper() for column in sales.columns]
        sales.columns = [column.replace('.', '') for column in sales.columns]
        sales.columns = [column.replace(' ', '_') for column in sales.columns]
        sales = sales.groupby(['CO','DESC_CO','NRO_DOCUMENTO','REF_COMBINADA','FECHA'])[['CANTIDAD_INV','SUMA_DE_VLR_BRUTO','SUMA_DE_VLR_SUBTOTAL']].sum().reset_index()
        sales['ID'] = sales['CO'].astype(str)+':'+sales['NRO_DOCUMENTO']+':'+sales['REF_COMBINADA']
        sales["DESCUENTO(%)"] = (sales['SUMA_DE_VLR_BRUTO']-sales['SUMA_DE_VLR_SUBTOTAL'])/sales['SUMA_DE_VLR_BRUTO']
        sales['PRECIO'] = sales['SUMA_DE_VLR_BRUTO']/sales['CANTIDAD_INV']
        sales['MES'] = sales['FECHA'].dt.month
        sales['ANIO'] = sales['FECHA'].dt.year
        sales['DIA'] = sales['FECHA'].dt.weekday
        sales = sales.rename(columns={
            'CO':'CODIGO_TIENDA',
            'DESC_CO':'TIENDA',
            'REF_COMBINADA':'PROD_REF',
            'CANTIDAD_INV':'CANTIDAD',
            'SUMA_DE_VLR_BRUTO':'SUBTOTAL',
            'SUMA_DE_VLR_SUBTOTAL':'TOTAL',
        })
        sales = sales[['ID','NRO_DOCUMENTO','FECHA','CODIGO_TIENDA','TIENDA','PROD_REF','CANTIDAD','PRECIO',
                'SUBTOTAL','DESCUENTO(%)','TOTAL','ANIO','MES','DIA']]
        return sales

    def __clean_stock(self,stock):
        stock.columns = [column.upper() for column in stock.columns]
        stock.columns = [column.replace('.', '') for column in stock.columns]
        stock.columns = [column.replace(' ', '_') for column in stock.columns]

        stock = stock.rename(columns={
            'EXT_1_DETALLE':'DETALLE_1',
            'EXT_2_DETALLE':'DETALLE_2',
            'REF_COMBINADA':'REF',
            'REFERENCIA':'ID',
            'DISP':'CANTIDAD',
            'DEPARTAMENTO':'CATEGORIA'
        })

        regex = '^([A-Z0-9]+\s\-\s)+'
        stock.CATEGORIA = stock.CATEGORIA.str.replace(regex,'',regex=True)
        stock.SUBCATEGORIA = stock.SUBCATEGORIA.str.replace(regex,'',regex=True)

        stock = stock[['ID','REF','CANTIDAD','CATEGORIA','SUBCATEGORIA','DETALLE_1','DETALLE_2']]
        return stock

    def __create_merges(self,sales,products,stock):
        sales_prod = sales.merge(products, left_on='PROD_REF', right_on='REF')
        stock_prod = stock.drop(columns=['CATEGORIA','SUBCATEGORIA']).merge(products, on='REF', how='left')
        return sales_prod, stock_prod

    def __create_categories(self,sales_prod):
        pareto_subcat = []
        temp = sales_prod.groupby('SUBCATEGORIA')["CANTIDAD"].sum().sort_values(ascending=False)
        totalSales = temp.sum()
        pareto = totalSales*0.8
        counter = 0

        temp = temp.to_frame().reset_index()
        for _, row in temp.iterrows():
            counter += row["CANTIDAD"]
            pareto_subcat.append(row["SUBCATEGORIA"])
            if counter >= pareto:
                break
        return pareto_subcat

    def __add_pos_cols(self,df,categories):
        df["SUBCATEGORIA_POS"] = df.apply(lambda row: row["SUBCATEGORIA"] if row["SUBCATEGORIA"] in categories else "OTROS",axis = 1 )
        df['COLOR_POS'] = np.where(df["COLOR"].isin(['NEGRO', 'GRIS', 'CAFE', 'BLANCO', 'AZUL', 'MIEL', 'BEIGE', 'CRISTAL',
            'ROJO', 'AMARILLO']), df["COLOR"], 'OTRO')
        return df

    def __create_references(self,sales_prod,products):
        references = sales_prod.groupby('REF').aggregate(
                CANTIDAD=pd.NamedAgg(column="CANTIDAD", aggfunc="sum"),
                TOTAL=pd.NamedAgg(column="TOTAL", aggfunc="sum"),
                PRECIO_PROMEDIO=pd.NamedAgg(column='PRECIO',aggfunc='mean'),
                DESCUENTO_PROMEDIO=pd.NamedAgg(column='DESCUENTO(%)', aggfunc= 'mean')
            ).reset_index().merge(products, on='REF').sort_values(by='CANTIDAD', ascending=False)
        ref_materials = references.groupby(['MATERIAL'])['CANTIDAD'].sum().sort_values(ascending=False)
        cumpperce = ref_materials.cumsum()/ref_materials.sum()*100
        ref_materials = cumpperce[cumpperce<91].to_frame().rename(columns={'CANTIDAD':'CANTIDAD(%)'})
        return references, ref_materials

    def __df_mat_mod(self,df,ref_materials):
        df['MATERIAL_POS'] = df['MATERIAL']
        df['MATERIAL_POS'] = df.apply(lambda x: x['MATERIAL'] if x['MATERIAL'] in ref_materials.index else "OTROS",axis=1)
        return df

    def __init__(self, isExternal=False):
        if(isExternal == True):
            path = '../'
        else:
            path = ''
        stock = pd.read_csv(path+'Data/ExistenciasNew.csv')
        sales = pd.read_csv(path+'Data/FacturacionCorregida.csv',parse_dates=['Fecha'],dayfirst=True ,sep=';')
        products = pd.read_csv(path+'Data/MaestroCorregido.csv', sep=';')

        products = self.__clean_products(products)
        sales = self.__clean_sales(sales)
        stock = self.__clean_stock(stock)
        sales_prod, stock_prod = self.__create_merges(sales,products,stock)
        categories = self.__create_categories(sales_prod)

        sales_prod = self.__add_pos_cols(sales_prod,categories)
        products = self.__add_pos_cols(products,categories)
        stock_prod = self.__add_pos_cols(stock_prod,categories)

        references, ref_materials = self.__create_references(sales_prod,products)

        self.products = self.__df_mat_mod(products,ref_materials)
        self.sales_prod = self.__df_mat_mod(sales_prod,ref_materials)
        self.stock_prod = self.__df_mat_mod(stock_prod,ref_materials)
        self.references = self.__df_mat_mod(references,ref_materials)

        self.all_incorporated_df = None
        self.all_incorporated_lag_df = None
        self.final_df_future = None
        self.join_lag_future = None
        self.full_data = None
        self.full_data_lag = None
        self.num_shift = -1
        
        self.grouped_sales=None
        demand2, self.discontinued, self.demand_classifier, self.classifier=self.demand_data(sales_prod.FECHA.min(),sales_prod.FECHA.max())

    def demand_data(self, start_date, end_date,save=False):
        self.demand_load = True
        sales_prod=self.sales_prod

        if (start_date is None or start_date == ""):
            start_date = sales_prod['FECHA'].min()
        
        if (end_date is None or end_date == ""):
            end_date = sales_prod['FECHA'].max()

        mask = (sales_prod['FECHA'] > start_date) & (sales_prod['FECHA'] <= end_date)
        sales_prod = sales_prod.loc[mask]
        demand = sales_prod[sales_prod['VIGENCIA']!='DESCONTINUADO'].copy()
        demand['YY_MM'] = demand['FECHA'].dt.strftime('%y-%m')

        dicts = {}
        for i,j in enumerate(demand['YY_MM'].sort_values().unique()):
            dicts[i] = j
            
        demand = demand.groupby(['PROD_REF','YY_MM'])['CANTIDAD'].sum().reset_index()
        demand = demand.pivot(index='PROD_REF',columns='YY_MM').fillna(0)
        demand['N_LAST'] = demand.apply(lambda x: np.where(x)[0][-1] ,axis=1)
        demand['LAST'] = demand['N_LAST'].map(dicts)
        demand['N_FIRST'] = demand.apply(lambda x: np.where(x)[0][0] ,axis=1)
        demand['FIRST'] = demand['N_FIRST'].map(dicts)
        demand['PER_LAST-FIRST'] = demand['N_LAST']-demand['N_FIRST']+1
        demand['PER_SIN_INFO'] = len(demand.columns[0:-5])-demand['N_LAST']-1
        v0 = demand[demand.columns[0:-5]].values
        v1 = np.where(v0 > 0, v0, np.nan)
        demand['DEMAND_BUCKETS'] = np.count_nonzero(v1>0, axis=1)-1
        demand['TOTAL_PER'] = np.count_nonzero(v1, axis=1)-demand['N_FIRST']-1
        demand['ADI'] = demand['TOTAL_PER']/demand['DEMAND_BUCKETS']
        demand['CV2'] = (np.nanstd(v1, axis=1)/np.nanmean(v1, axis=1))**2
        demand2 = demand.set_axis(demand.columns.map(''.join), axis=1, inplace=False).reset_index()
        demand2 = demand2[['PROD_REF','N_LAST','LAST','N_FIRST','FIRST','PER_LAST-FIRST','PER_SIN_INFO','DEMAND_BUCKETS','TOTAL_PER','ADI','CV2']]
        features = sales_prod[sales_prod['VIGENCIA']!='DESCONTINUADO']
        columnsx = ['PROD_REF','DESCRIPCION','ITEM', 'CATEGORIA', 'SUBCATEGORIA', 'VIGENCIA',
            'ORIGEN', 'ESTILO','SUBCATEGORIA_POS', 'COLOR_POS',
            'MATERIAL_POS']
        features = features[columnsx].drop_duplicates()
        features
        demand2 = demand2.merge(features, how='left', on='PROD_REF')

        def classifier_fun(df):
            ADI = df['ADI']
            CV2  = df['CV2']
            
            if (ADI < 1.32 and CV2 < 0.49):
                a = 'Smooth'
            elif (ADI >= 1.32 and CV2 < 0.49):
                a = 'Intermittent'
            elif (ADI < 1.32 and CV2 >= 0.49):
                a = 'Erratic'
            else:
                a = 'Lumpy'
            return a

        demand2['CLASSIFIER'] = demand2.apply(classifier_fun, axis=1)
        discontinued = demand2[demand2['N_LAST']<12]
        discontinued = discontinued[['PROD_REF','DESCRIPCION','CATEGORIA','SUBCATEGORIA_POS','FIRST','LAST']]
        demand2 = demand2[demand2['N_LAST']>=12]
        classifier = demand2[['PROD_REF','CLASSIFIER']]
        demand3 = demand['CANTIDAD'].stack().reset_index().rename(columns={0: 'CANTIDAD'})
        demand3 = demand3.merge(demand2, how='right', on='PROD_REF')
        if save:
            self.last_demand_classifier=demand3
            self.last_classifier=classifier
        return demand2, discontinued, demand3, classifier
    
    def data_no_outliers(self):
        if self.grouped_sales is None:
            sales_prod = self.sales_prod
            sales_prod['PUESTOS'].fillna(0,inplace=True)
            
            columns_LD = ['REF','TIENDA', 'PRECIO', 'SUBTOTAL','DESCUENTO(%)','TOTAL','CANTIDAD','ANIO','MES','CATEGORIA','SUBCATEGORIA_POS','VIGENCIA','ORIGEN','ESTILO','MATERIAL_POS','ACABADO','COLOR_POS','ALTO','AREA','PUESTOS']
            sales_prod_LD = sales_prod[columns_LD]

            grouped_sales = sales_prod_LD.groupby(['ANIO','MES','REF','TIENDA']).agg({'PRECIO':'mean','SUBTOTAL':'sum','DESCUENTO(%)':'mean','TOTAL':'sum','CANTIDAD':'sum','ALTO':'first','AREA':'first','PUESTOS':'first','COLOR_POS':'first','CATEGORIA':'first','SUBCATEGORIA_POS':'first','VIGENCIA':'first','ORIGEN':'first','ESTILO':'first','MATERIAL_POS':'first','ACABADO':'first'}).reset_index().sort_values(by=['ANIO','MES'])
            
            covid = grouped_sales[['ANIO','MES']].drop_duplicates().reset_index(drop=True)
            factors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,1,1,1,2,2,1,1,2,2,1,1,1]
            covid['F_COVID']= factors
            
            grouped_sales = grouped_sales.merge(covid,on=['ANIO','MES'])
            grouped_sales['DATE'] = grouped_sales['ANIO'].astype(str) + '-' + grouped_sales['MES'].astype(str).str.zfill(2)
            
            def remove_ventas_anormales(df):
                return df.query('CANTIDAD<20')
            
            self.grouped_sales = remove_ventas_anormales(grouped_sales).reset_index(drop=True)
                
        return self.grouped_sales

    def all_data(self):
        if self.all_incorporated_df is None:
            data = self.data_no_outliers()
            data['DATE'] = data['ANIO'].astype(str) + '-' + data['MES'].astype(str).str.zfill(2)

            df = data.pivot_table(index=['REF','TIENDA'],columns=['DATE','ANIO','MES'],values='CANTIDAD',aggfunc='sum').reset_index()
            df = pd.melt(df,id_vars=['REF','TIENDA'])

            df = df.sort_values(['REF','DATE'])
            df = df.rename(columns={'value':'CANTIDAD'})
            df = df.reset_index(drop=True).fillna(0)

            aux = data.drop(columns=['ANIO','MES','CANTIDAD']).groupby(['REF','DATE','TIENDA']).agg({'PRECIO':'mean','DESCUENTO(%)':'mean','AREA':'first','ALTO':'first','PUESTOS':'first', 'COLOR_POS':'first','SUBCATEGORIA_POS':'first','MATERIAL_POS':'first','ACABADO':'first','CATEGORIA':'first','ORIGEN':'first','F_COVID':'first','VIGENCIA':'first'}).reset_index()
            df = df.merge(aux,on=['REF','DATE','TIENDA'],how='left',validate='1:1')
            prods=aux[['REF','AREA','ALTO','PUESTOS', 'COLOR_POS','SUBCATEGORIA_POS','MATERIAL_POS','ACABADO','CATEGORIA','ORIGEN','VIGENCIA']].drop_duplicates()
            df = df[['REF','TIENDA','DATE','ANIO','MES','CANTIDAD','PRECIO','DESCUENTO(%)']]
            df = df.merge(prods,on='REF')
            df = df.sort_values(['ANIO','MES']).reset_index(drop=True)

            Dfinal=df.sort_values(['DATE'])
            covid=self.grouped_sales[['ANIO','MES']].drop_duplicates().reset_index(drop=True)
            aux2=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,1,1,1,2,2,1,1,2,2,1,1,1]
            covid['F_COVID']=aux2
            Dfinal=Dfinal.merge(covid,on=['ANIO','MES'])


            Dfinal['PRECIO']=Dfinal.groupby(['REF','TIENDA'])['PRECIO'].apply(lambda group: group.interpolate(method='index').ffill().bfill())
            Dfinal['DESCUENTO(%)']=Dfinal.groupby(['REF','TIENDA'])['DESCUENTO(%)'].apply(lambda group: group.interpolate(method='index').ffill().bfill())
            self.all_incorporated_df=Dfinal.dropna().query('DATE != "2021-04"').reset_index(drop=True) #drops only 3% of all data for modeling purposes
        return self.all_incorporated_df


    def all_data_lag(self,num=12):#change num for selection of laggy months
        if self.all_incorporated_lag_df is None or num!=self.num_shift:
            def df_lag_generator(n):
                df_lag=self.all_data().copy()
                for i in range(n):
                    df_lag['CANTIDAD_{}'.format(i+1)]=df_lag.groupby(['REF','TIENDA'])[['CANTIDAD']].shift(i+1)
                return df_lag
        
            self.all_incorporated_lag_df=df_lag_generator(num).dropna().reset_index(drop=True)
            for i in range(1,num):
                self.all_incorporated_lag_df['DIFF_{}'.format(i)]=(self.all_incorporated_lag_df['CANTIDAD_{}'.format(i)]-self.all_incorporated_lag_df['CANTIDAD_{}'.format(1+i)])
        self.num_shift=num
        return self.all_incorporated_lag_df

    
    def data_forecasting_2021(self):
        ##sacar productos descontinuados
        if self.final_df_future is None:
            aux=self.all_data()#.query('VIGENCIA != "DESCONTINUADO"')
            aux=aux.groupby(['REF','TIENDA']).agg({'PRECIO':'mean','DESCUENTO(%)':'mean','AREA':'first',
                                                        'ALTO':'first','PUESTOS':'first', 'COLOR_POS':'first', 
                                                        'SUBCATEGORIA_POS':'first','MATERIAL_POS':'first','ACABADO':'first',
                                                        'CATEGORIA':'first','ORIGEN':'first'}).reset_index()
            # 2021 future months and covid
            months=[4,5,6,7,8,9,10,11,12]# 4 because there is no complete data, better to ignore it, then to predict.
            covid=[0,0,0,0,0,0,0,0,0]
            aux0=aux[['REF','TIENDA']].copy()
            for m,c in zip(months,covid):
                aux0[m]=c
            #display(aux0)
            aux1=pd.melt(aux0,id_vars=['REF','TIENDA'],var_name='MES',value_name='F_COVID')
            #display(aux1.sort_values(by=['REF','TIENDA']))
            final_df_future=aux1.merge(aux,on=['REF','TIENDA'],how='left')
            final_df_future['ANIO']=2021
            final_df_future['DATE'] = final_df_future['ANIO'].astype(str) + '-' +final_df_future['MES'].astype(str).str.zfill(2)
            self.final_df_future=final_df_future.sort_values(['ANIO','MES']).reset_index(drop=True)
        return self.final_df_future

    
    def data_forecasting_2021_lag(self,num=12):# change num if you want different months 
        if self.join_lag_future is None or num!=self.num_shift:
            pasado=self.all_incorporated()
            futuro=self.data_forecasting_2021()    
            join=pd.concat([pasado,futuro],axis=0).sort_values(['DATE'])
            
            def df_lag_generator(n):
                df_lag=join.copy()
                for i in range(n):
                    df_lag['CANTIDAD_{}'.format(i+1)]=df_lag.groupby(['REF','TIENDA'])[['CANTIDAD']].shift(i+1)
                return df_lag
            #num=12 # change num if you want different months
            join_lag=df_lag_generator(num).reset_index(drop=True)
            aux_index=join_lag.query('DATE=="2021-04"').index[0]
            join_lag_future = join_lag[aux_index:].copy()
            for i in range(1,num):
                join_lag_future['DIFF_{}'.format(i)]=(join_lag_future['CANTIDAD_{}'.format(i)]-join_lag_future['CANTIDAD_{}'.format(1+i)])
            self.join_lag_future=join_lag_future
            self.num_shift=num
        return self.join_lag_future
                
    def data_future(self):
        if self.full_data is None:
            sales = self.sales_prod.copy()
            prods = self.products.drop_duplicates().copy()

            data = self.data_no_outliers()
            
            pasado = data.pivot_table(index='REF',columns=['DATE','ANIO','MES','TIENDA'],values='CANTIDAD',aggfunc='sum').reset_index()
            pasado = pd.melt(pasado,id_vars='REF')

            pasado = pasado.sort_values(['REF','DATE'])
            pasado = pasado.rename(columns={'value':'CANTIDAD'})
            pasado = pasado.reset_index(drop=True).fillna(0)

            pasado = pasado.merge(data.drop(columns=['CANTIDAD','ANIO','MES']).groupby(['REF','DATE','TIENDA']).agg({'PRECIO':'mean','DESCUENTO(%)':'mean','F_COVID':'first'}),on=['REF','DATE','TIENDA'],how='left',validate='1:1')
            pasado = pasado[['REF','TIENDA','DATE','ANIO','MES','CANTIDAD','PRECIO','DESCUENTO(%)','F_COVID']]

            covid_aux = self.data_no_outliers()[['DATE','F_COVID']].drop_duplicates()
            covid_aux = covid_aux.set_index('DATE')
            pasado = pasado.set_index('DATE')
            pasado.update(covid_aux)
            pasado.reset_index(inplace=True)

            promedios_aux = sales.groupby(['REF']).agg({'PRECIO':'mean','DESCUENTO(%)':'mean','DESC_LARGA':'first'})[['PRECIO','DESCUENTO(%)']]
            pasado = pasado.set_index('REF')
            pasado.update(promedios_aux, overwrite=False)
            pasado.reset_index(inplace=True)

            pasado = pasado.merge(prods,on='REF',validate='m:1')
            pasado['PUESTOS'].fillna(0,inplace=True)
            pasado = pasado.sort_values(['ANIO','MES']).reset_index(drop=True)

            past_dates = sales[['ANIO','MES']].sort_values(by=['ANIO','MES']).reset_index(drop=True)
            past_dates.drop_duplicates(inplace=True)
            past_dates['DATE'] = past_dates.ANIO.astype('str') + '-' + past_dates.MES.astype('str').str.zfill(2)
            past_dates = past_dates.drop(columns=['ANIO','MES'])
            past_dates.drop(past_dates.tail(1).index,inplace=True)

            new_dates = past_dates.sort_values(by='DATE',ascending=False).reset_index(drop=True).iloc[1:13]
            new_dates['DATE'] = pd.to_datetime(new_dates.DATE) + pd.DateOffset(months=13)
            new_dates.DATE = new_dates.DATE.dt.year.astype('str') + '-' + new_dates.DATE.dt.month.astype('str').str.zfill(2)

            # Fix past sales last month overlap
            pasado = pasado[pasado.DATE != str(new_dates.tail(1).values[0][0])]

            past_sales = pasado.copy().query('VIGENCIA != "DESCONTINUADO"')
            past_sales = past_sales.groupby(['REF','TIENDA']).agg({'PRECIO':'mean','DESCUENTO(%)':'mean',
                'AREA':'first','ALTO':'first','PUESTOS':'first', 'COLOR_POS':'first', 
                'SUBCATEGORIA_POS':'first','MATERIAL_POS':'first','ACABADO':'first',
                'CATEGORIA':'first','ORIGEN':'first'}
            ).reset_index()

            covid = [0,0,0,0,0,0,0,0,0,0,0,0]
            min_sales = past_sales[['REF','TIENDA']].copy()
            for m,c in zip(new_dates.values.tolist(),covid):
                min_sales[m]=c

            melt_sales = pd.melt(min_sales,id_vars=['REF','TIENDA'],var_name='DATE',value_name='F_COVID')
            melt_sales['ANIO'] = pd.to_datetime(melt_sales.DATE).dt.year
            melt_sales['MES'] = pd.to_datetime(melt_sales.DATE).dt.month

            futuro = melt_sales.merge(past_sales,on=['REF','TIENDA'],how='left',validate='m:1')
            futuro.sort_values(by=['ANIO','MES'],ascending=True,inplace=True)
            futuro.reset_index(drop=True,inplace=True)
            futuro = futuro[['REF','TIENDA','DATE','ANIO','MES','PRECIO','DESCUENTO(%)','F_COVID','AREA','ALTO','PUESTOS','COLOR_POS','SUBCATEGORIA_POS','MATERIAL_POS','ACABADO','ORIGEN','CATEGORIA']]
            futuro['CANTIDAD'] = 0
            futuro = futuro.fillna(0)

            full_data = pd.concat([pasado.copy(),futuro.copy()]).reset_index(drop=True)
            full_data = full_data.drop(columns=['ITEM','DESCRIPCION','SUBCATEGORIA','VIGENCIA','ESTILO','MATERIAL','COLOR','FONDO','DESC_LARGA'])
            full_data_limit = len(futuro)
            
            self.full_data = full_data
            self.full_data_limit = full_data_limit

        return self.full_data, self.full_data_limit
    
    def all_data_future_lag(self,num=12):
        if self.full_data_lag is None or num!=self.num_shift:
            data, index = self.data_future()

            lag_data = data.copy()

            for i in range(num):
                lag_data['CANTIDAD_{}'.format(i+1)] = lag_data.groupby(['REF','TIENDA'])[['CANTIDAD']].shift(i+1)
            lag_data = lag_data.reset_index(drop=True)

            past = lag_data[:-index].copy().dropna().reset_index(drop=True)
            fut = lag_data[-index:].reset_index(drop=True).fillna(0)

            for i in range(1,num):
                past['DIFF_{}'.format(i)] = (past['CANTIDAD_{}'.format(i)] - past['CANTIDAD_{}'.format(1+i)])
                fut['DIFF_{}'.format(i)] = (fut['CANTIDAD_{}'.format(i)] - fut['CANTIDAD_{}'.format(1+i)])

            self.full_data_lag = pd.concat([past,fut], axis=0)
            self.index = index
            self.num_shift = num

        return self.full_data_lag, self.index