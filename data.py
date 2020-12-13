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

class data():

    def __init__(self):
        self.df, self.conf_dict = self.read_data()
        self.df0 = self.df.copy()
        self.desc_stats_num, self.desc_stats_cat = self.descriptive_statistics()

    def read_data(self):

        conf_file = "config.yaml"
        Sample_Size =  10000
        conf_dict = yaml.load(open(conf_file), Loader=yaml.FullLoader)
        
        # Read in data from local file or SQL server
        # if 'DataSource' not in conf_dict:
        #     df=pd.read_csv(conf_dict['DataFilePath'][0], skipinitialspace=True)
        # else:
        #     import pyodbc
        #     cnxn = pyodbc.connect('driver=ODBC Driver 17 for SQL Server;server={};port=1433;database={};Uid={};Pwd={}'.format(
        #             conf_dict['Server'], conf_dict['Database'],conf_dict['Username'],conf_dict['Password']))
        #     df = pd.read_sql(conf_dict['Query'],cnxn)

        # Fix data source for testing and development
        df = pd.read_csv('data/titanic.csv')

        # Making sure that we are not reading any extra column
        df = df[[each for each in df.columns if 'Unnamed' not in each]]

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


    def descriptive_statistics(self):
        def num_missing(x):
            return len(x.index)-x.count()

        def num_unique(x):
            return len(np.unique(x))

        temp_df = self.df0.describe().T
        missing_df = pd.DataFrame(self.df0.apply(num_missing, axis=0))
        missing_df.columns = ['missing']
        unq_df = pd.DataFrame(self.df0.apply(num_unique, axis=0))
        unq_df.columns = ['unique']

        types_df = pd.DataFrame(self.df0.dtypes)
        types_df.columns = ['DataType']

        summary_df_num = temp_df.join(missing_df).join(unq_df)#.join(types_df)
        summary_df_num.index = summary_df_num.index.set_names(['Column name'])

        col_names = list(types_df.index) #Get all col names
        num_cols = len(col_names)
        index = range(num_cols)

        cat_index = []
        for i in index: #Find the indices of columns in Categorical columns
            if col_names[i] in self.conf_dict['CategoricalColumns']:
                cat_index.append(i)

        summary_df_cat = missing_df.join(unq_df)#.join(types_df.iloc[cat_index], how='inner')
        summary_df_cat.index = summary_df_cat.index.set_names(['Column name'])

        return summary_df_num.reset_index(), summary_df_cat.reset_index()


    def target_distribution(self, target):
        return pd.DataFrame(self.df[target].value_counts()).reset_index()

    @staticmethod
    def shapiro_test(x):
        p_val = round(stats.shapiro(x)[1], 6)
        status = 'passed'
        color = 'blue'
        if p_val < 0.05:
            status = 'failed'
            color = 'red'
        return status, color, p_val