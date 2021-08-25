import pandas as pd
class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataSingleton(metaclass=SingletonMeta):
    
    def __clean_products(products):
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

    def __clean_sales(sales):
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

    def __clean_stock(stock):
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

    def __create_merges(sales,products):
        sales_prod = sales.merge(products, left_on='PROD_REF', right_on='REF')
        stock_prod = stock.drop(columns=['CATEGORIA','SUBCATEGORIA']).merge(products, on='REF', how='left')
        return sales_prod, stock_prod

    def __create_subcategories_list(sales_prod):
        subcategories_list = []
        temp = sales_prod.groupby('SUBCATEGORIA')["CANTIDAD"].sum().sort_values(ascending=False)
        totalSales = temp.sum()
        pareto = totalSales*0.8
        counter = 0
    
        temp = temp.to_frame().reset_index()
        for index, row in temp.iterrows():
            counter += row["CANTIDAD"]
            subcategories_list.append(row["SUBCATEGORIA"])
            if counter >= pareto:
                break
        return subcategories_list

    def __create_materials_list(sales_prod):
        materials_list = sales_prod.groupby(['MATERIAL'])['CANTIDAD'].sum().sort_values(ascending=False)
        cumpperce = materials_list.cumsum()/materials_list.sum()*100
        materials_list = cumpperce[cumpperce<91].to_frame().rename(columns={'CANTIDAD':'CANTIDAD(%)'})
        return materials_list

    def __create_consolidated(sales_prod):
        consolidated = sales_prod.groupby('REF').aggregate(
            CANTIDAD=pd.NamedAgg(column="CANTIDAD", aggfunc="sum"),
            TOTAL=pd.NamedAgg(column="TOTAL", aggfunc="sum"), 
            PRECIO_PROMEDIO=pd.NamedAgg(column='PRECIO',aggfunc='mean'),
            DESCUENTO_PROMEDIO=pd.NamedAgg(column='DESCUENTO(%)', aggfunc= 'mean')
        ).reset_index().merge(products, on='REF').sort_values(by='CANTIDAD', ascending=False)
        return consolidated

    def __add_category_pos(row):
        if row["SUBCATEGORIA"] in subcategories_list:
            index = row["SUBCATEGORIA"]
        else:
            index = "OTROS"
        return index

    def __add_pos_cols(arr):
        arr["SUBCATEGORIA_POS"] = arr.apply(add_category_pos,axis = 1 )
        arr['COLOR_POS'] = np.where(
            arr["COLOR"].isin(['NEGRO','GRIS','CAFE', 'BLANCO','AZUL','MIEL','BEIGE','CRISTAL','ROJO','AMARILLO']),
            arr["COLOR"],
            'OTRO'
        )
        arr['MATERIAL_POS']=np.where(arr['MATERIAL'].isin(materials_list.index), arr['MATERIAL'], 'OTRO')

    def __init__(self):
        stock = pd.read_csv('Proyecto/Data/ExistenciasNew.csv')
        sales = pd.read_csv('Proyecto/Data/FacturacionCorregida.csv',parse_dates=['Fecha'],dayfirst=True ,sep=';')
        products = pd.read_csv('Proyecto/Data/MaestroCorregido.csv', sep=';')

        self.products = self.__clean_products(products)
        self.sales = self.__clean_sales(sales)
        self.stock = self.__clean_stock(stock)

        self.sales_prod, self.stock_prod = self.__create_merges(sales,products)
        self.groupby_sales = self.__create_consolidated(sales_prod)

        self.subcategories_list = self.__create_subcategories_list(sales_prod)
        self.materials_list = self.__create_materials_list(sales_prod)

        self.__add_pos_cols(sales_prod)
        self.__add_pos_cols(products)
        self.__add_pos_cols(stock_prod)
        self.__add_pos_cols(groupby_sales)
    