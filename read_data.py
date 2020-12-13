import pandas as pd
import numpy as np
import os
import collections
import matplotlib
import io
import sys
import operator
import yaml

import scipy.stats as stats
from statsmodels.graphics.mosaicplot import mosaic
import statsmodels.api as sm
from statsmodels.formula.api import ols
import os
from string import Template
from functools import partial
from collections import OrderedDict

conf_file = "config.yaml"
Sample_Size =  10000
conf_dict = yaml.load(open(conf_file), Loader=yaml.FullLoader)

class data():

    def __init__(self):
        self.data = self.read_data()

    def read_data(self):
        
        # Read in data from local file or SQL server
        if 'DataSource' not in conf_dict:
            df=pd.read_csv(conf_dict['DataFilePath'][0], skipinitialspace=True)
        else:
            import pyodbc
            cnxn = pyodbc.connect('driver=ODBC Driver 17 for SQL Server;server={};port=1433;database={};Uid={};Pwd={}'.format(
                    conf_dict['Server'], conf_dict['Database'],conf_dict['Username'],conf_dict['Password']))
            df = pd.read_sql(conf_dict['Query'],cnxn)

        # Making sure that we are not reading any extra column
        df = df[[each for each in df.columns if 'Unnamed' not in each]]

        # Sampling Data if data size is larger than 10k
        df0 = df # df0 is the unsampled data. Will be used in data exploration and analysis where sampling is not needed
                # However, keep in mind that your final report will always be based on the sampled data. 
        if Sample_Size < df.shape[0]:
            df = df.sample(Sample_Size)

        # change float data types
        if 'FloatDataTypes' in conf_dict:   
            for col_name in conf_dict['FloatDataTypes']:
                df[col_name] = df[col_name].astype(float)      

        # Getting the list of categorical columns if it was not there in the yaml file
        if 'CategoricalColumns' not in conf_dict:
            conf_dict['CategoricalColumns'] = list(set(list(df.select_dtypes(exclude=[np.number]).columns)))

        # Getting the list of numerical columns if it was not there in the yaml file
        if 'NumericalColumns' not in conf_dict:
            conf_dict['NumericalColumns'] = list(df.select_dtypes(include=[np.number]).columns)    

        # Exclude columns that we do not need
        if 'ColumnsToExclude' in conf_dict:
            conf_dict['CategoricalColumns'] = list(set(conf_dict['CategoricalColumns'])-set(conf_dict['ColumnsToExclude']))
            conf_dict['NumericalColumns'] = list(set(conf_dict['NumericalColumns'])-set(conf_dict['ColumnsToExclude']))

        # Ordering the categorical variables according to the number of unique categories
        filtered_cat_columns = []
        temp_dict = {}
        for cat_var in conf_dict['CategoricalColumns']:
            temp_dict[cat_var] = len(np.unique(df[cat_var]))
        sorted_x = sorted(temp_dict.items(), key=operator.itemgetter(0), reverse=True)
        conf_dict['CategoricalColumns'] = [x for (x,y) in sorted_x]
        
        return df, conf_dict
