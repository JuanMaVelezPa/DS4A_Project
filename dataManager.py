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
        products = products[['ITEM','REF','DESCRIPCION','CATEGORIA','SUBCATEGORIA','VIGENCIA','ORIGEN',
                        'ESTILO','MATERIAL','ACABADO','PUESTOS','COLOR','ANCHO','ALTO','FONDO','DESC_LARGA']]
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
        df['MATERIAL_POS'] = df.apply(lambda x: x['MATERIAL'] if x['MATERIAL'] in ref_materials.index else "otros",axis=1)
        return df

    def __init__(self):
        stock = pd.read_csv('Data/ExistenciasNew.csv')
        sales = pd.read_csv('Data/FacturacionCorregida.csv',parse_dates=['Fecha'],dayfirst=True ,sep=';')
        products = pd.read_csv('Data/MaestroCorregido.csv', sep=';')

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