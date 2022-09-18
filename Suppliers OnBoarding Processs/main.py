"""
Prerequisites 

Deep-translator 1.8.3 
https://pypi.org/project/deep-translator/

pip install -U deep-translator

"""

import os
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator

pd.set_option('display.max_rows', None)

#Print data frame rows, default 5
def print_data(data,rows=5):
    display(data.head(rows)) 
    
#Load the json file    
def load_json_data():
    df = pd.read_json('supplier_car.json') 
    return df  

# Clean (drop 'entity_id') and sort data by 'ID','Attribute Names'
def clean_sort_data(data):
    df = data.drop(['entity_id'], axis=1).sort_values(['ID','Attribute Names']).reset_index()
    return df

#Explore data. Check for unique values
def explore_data(data):
    print_data(data)
    display(data['ID'].unique().size)
    display(data['Attribute Names'].unique().size)
    display(data.shape)
    
# Split data into two dataframes. Use pivot to reshape data    
def split_pivot_data(data):  
    df1 = data[['ID','MakeText','TypeName','TypeNameFull','ModelText','ModelTypeText']].drop_duplicates().set_index('ID')
        
    df2 = data.pivot(index='ID', 
                     columns='Attribute Names', 
                     values='Attribute Values').reset_index().rename_axis(None, axis=1).set_index('ID')
    
    return df1, df2   

#Merge two data sets on 'ID'
def merge_data(dx,dy): 
    data = dx.merge(dy, on='ID')
    return data

#Map supplier data to target data
def map_to_target_data(data):
    return data[
    ['BodyTypeText',
     'BodyColorText',
     'ConditionTypeText',
     'City',
     'MakeText',
     'FirstRegYear',
     'Km',
     'ModelText',
     'ModelTypeText',
     'FirstRegMonth',
    'ConsumptionTotalText']].rename(columns={
                      'BodyTypeText' :'carType',
                      'ConditionTypeText':'condition',
                      'BodyColorText':'color',
                      'City':'city',
                      'MakeText':'make',
                      'FirstRegYear':'manufacture_year',
                      'Km':'mileage',
                      'ModelText':'model',
                      'ModelTypeText':'model_variant',
                      'FirstRegMonth':'manufacture_month',
                      'ConsumptionTotalText':'fuel_consumption_unit'})  

#Translate value using GoogleTranslator. Return dictonary as de=>en
def translate(data, column):
    items_de = data[~data[column].isna()][column].unique()
    items = {}
    for x in items_de:
        items[x] = GoogleTranslator(source='de', target='en').translate(x).capitalize()
    return items

# Make the normalization steps. Load translations into dictonary as de=>en. Use lamda function for bulk inline transformation
def normalize_data(data):
    
    colors = translate(data,'color')
    carTypes = translate(data,'carType')
    conditions = translate(data,'condition')
    
    data['color']=data['color'].apply(lambda x: colors[x] if colors.get(x) != None else x)
    data['carType']=data['carType'].apply(lambda x: carTypes[x] if carTypes.get(x) != None else x)
    data['condition']=data['condition'].apply(lambda x: conditions[x] if conditions.get(x) != None else x)
    data['fuel_consumption_unit']=data['fuel_consumption_unit'].apply(lambda x: 'l_km_consumption' if 'l/100km' in x else x)

    return data  

#Fill the missing columns to achive the same schema as target
def integrate_data(data):
    
    data.insert(3, 'currency', 'null')
    data.insert(4, 'drive', 'null')
    data.insert(6, 'country', 'null')
    data.insert(10, 'mileage_unit', 'null')
    data.insert(13, 'price_on_request', 'null')
    data.insert(14, 'type', 'null')
    data.insert(15, 'zip', 'null')
    
    return data

# Output data frame to excel file
def output_to_excel(file, data_x, sheet):
    mode='w'
    if os.path.exists(file):
         mode='a'
        
    with pd.ExcelWriter(file, engine='openpyxl', mode=mode) as writer:  
        data_x.to_excel(writer, sheet_name=sheet, index=False)

if __name__ == '__main__':
    
    data = load_json_data()
    print_data(data)
    display(data.shape)
    
    file = 'Integrated_supplier_data.xlsx'
    if os.path.exists(file):
         os.remove(file)   

    #1. Pre-processing
    
    #Clean and sort the data
    data_cleaned = clean_sort_data(data)
    explore_data(data_cleaned)

    #Find the Model Id that have 18 attributes
    atributes_count = data.groupby(['ID'])['ID'].count().sort_values()
    print_data(atributes_count)

    #Split original data set in two data set 
    dx,dy = split_pivot_data(data_cleaned)
    print_data(dx)
    display(dx.shape)
    print_data(dy)
    display(dy.shape)

    #Merge two data sets into one
    pre_procesed_data = merge_data(dx,dy)
    print_data(pre_procesed_data)
    display(pre_procesed_data.shape)
    output_to_excel(file, pre_procesed_data,'1. Pre-processing')

    #2. Normalization 

     #Map pre-processed data to the target data
    mapped_data = map_to_target_data(pre_procesed_data)
    print_data(mapped_data)
    display(mapped_data.shape)

    #Normalize known column values
    normalized_data = normalize_data(mapped_data)
    print_data(normalized_data)
    display(normalized_data.shape)

    output_to_excel(file, normalized_data,'2. Normalization')

     #3. Integration

    # Transform the supplier data into target data schema
    integrated_data = integrate_data(normalized_data)
    print_data(integrated_data)
    display(integrated_data.shape)

    output_to_excel(file, integrated_data,'3. Integration')