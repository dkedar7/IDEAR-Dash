import matplotlib.pyplot as plt
import matplotlib
import scipy.stats as stats
from statsmodels.graphics.mosaicplot import mosaic

import statsmodels.api as sm
from statsmodels.formula.api import ols

import pandas as pd
import numpy as np
import scipy

class InteractionAnalytics():
    @staticmethod
    def rank_associations(df, conf_dict, col1, col2, col3):        
        try:
            col2 = int(col2)
            col3 = int(col3)
        except:
            pass

        # Passed Variable is Numerical
        if (col1 in conf_dict['NumericalColumns']) :
            if len(conf_dict['NumericalColumns'])>1:

                # Interaction with numerical variables
                df2 = df[conf_dict['NumericalColumns']]
                corrdf = df2.corr()
                corrdf = abs(corrdf) # get the absolute values of correlations since negative correlations also matter
                corrdf2 = corrdf[corrdf.index==col1].reset_index()[[each for each in corrdf.columns \
                                                      if col1 not in each]].unstack().sort_values(kind="quicksort", 
                                                                                                  ascending=False).head(col2)
                corrdf2 = corrdf2.reset_index()
                corrdf2.columns = ['Variable','level1', 'Correlation']
                metric_num = "R-squared"

                # Interaction with categorical variables
                etasquared_dict = {}
            if len(conf_dict['CategoricalColumns']) >= 1:
                for each in conf_dict['CategoricalColumns']:
                    mod = ols('{} ~ C({})'.format(col1, each),data=df[[col1,each]],missing='drop').fit()
                    aov_table = sm.stats.anova_lm(mod, typ=1)
                    esq_sm = aov_table['sum_sq'][0]/(aov_table['sum_sq'][0]+aov_table['sum_sq'][1])
                    etasquared_dict[each] = esq_sm

                topk_esq = pd.DataFrame.from_dict(etasquared_dict, orient='index').unstack().sort_values(\
                    kind = 'quicksort', ascending=False).head(col3).reset_index()
                topk_esq.columns = ['level_0', 'Variable', 'Correlation']
                metric_cat = 'Eta-Squared'

            return corrdf2, metric_num, topk_esq, metric_cat

        # Passed Variable is Categorical
        else:
            #Interaction with numerical variables
            if len(conf_dict['NumericalColumns']) >= 1:
                etasquared_dict = {}
                for each in conf_dict['NumericalColumns']:
                    mod = ols('{} ~ C({})'.format(each, col1), data = df[[col1,each]]).fit()
                    aov_table = sm.stats.anova_lm(mod, typ=1)
                    esq_sm = aov_table['sum_sq'][0]/(aov_table['sum_sq'][0]+aov_table['sum_sq'][1])
                    etasquared_dict[each] = esq_sm

                topk_esq = pd.DataFrame.from_dict(etasquared_dict, orient='index').unstack().sort_values(\
                    kind = 'quicksort', ascending=False).head(col2).reset_index()
                topk_esq.columns = ['level_0', 'Variable', 'Correlation']
                metric_num = 'Eta-Squared'

            # Interaction with categorical variables
            cramer_dict = {}
            if len(conf_dict['CategoricalColumns'])>1:
                for each in conf_dict['CategoricalColumns']:
                    if each !=col1:
                        tbl = pd.crosstab(df[col1], df[each])
                        chisq = stats.chi2_contingency(tbl, correction=False)[0]
                        try:
                            cramer = np.sqrt(chisq/sum(tbl))
                        except:
                            cramer = np.sqrt(chisq/tbl.values.sum())
                            pass
                        cramer_dict[each] = cramer

                topk_cramer = pd.DataFrame.from_dict(cramer_dict, orient='index').unstack().sort_values(\
                    kind = 'quicksort', ascending=False).head(col3).reset_index()
                topk_cramer.columns = ['level_0','Variable','Correlation']
                metric_cat = "Cramer's V"

            return topk_esq, metric_num, topk_cramer, metric_cat
        
    @staticmethod
    def NoLabels(x):
        return ''

    @staticmethod
    def categorical_relations(df, col1, col2):
        if col1 != col2:
            df2 = df[(df[col1].isin(df[col1].value_counts().head(10).index.tolist()))&(df[col2].isin(df[col2].value_counts().head(10).index.tolist())) ]
            df3 = pd.crosstab(df2[col1], df2[col2])
            df3 = df3+1e-8
        else:
            df3 = pd.DataFrame(df[col1].value_counts())[:10]

        return df3
    
    @staticmethod
    def numerical_relations(df, col1, col2):
        from statsmodels.nonparametric.smoothers_lowess import lowess
        x = df[col2]
        y = df[col1]

        # lowess
        lowess_results = pd.DataFrame(lowess(y, x))
        lowess_results.columns = ['x', 'lowess']

        #ols
        fit = np.polyfit(x, y, 1)
        fit1d = np.poly1d(fit)

        ols = pd.DataFrame(data={'x':x, 'ols':fit1d(x)})

        #Corr 
        corr = round(stats.pearsonr(x, y)[0], 6)

        return lowess_results, ols, corr
    
    @staticmethod
    def numerical_correlation(df, conf_dict, method):
        corr_df= df[conf_dict['NumericalColumns']].corr(method=method)        
        return corr_df
                
    @staticmethod
    def nc_relation(df, conf_dict, col1, col2):

        mod = ols('{} ~ {}'.format(col1, col2), data=df[[col1, col2]]).fit()
        aov_table = sm.stats.anova_lm(mod, typ=1)
        p_val = round(aov_table['PR(>F)'][0], 6)
        status = 'Passed'
        color = 'blue'
        if p_val < 0.05:
            status = 'Rejected'
            color = 'red'

        return status, p_val
    
    @staticmethod
    def pca_3d(df, conf_dict, col1, comp1, comp2):
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler

        num_numeric = len(conf_dict['NumericalColumns'])

        df2 = df[conf_dict['NumericalColumns']]
        X = StandardScaler().fit_transform(df2.values)
        pca = PCA(n_components = num_numeric)
        pca.fit(X) 

        explained_variance = pd.DataFrame(data={'Component':np.arange(1,(num_numeric+1),1),
                                               'Variance':pca.explained_variance_ratio_})

        Y_pca = pd.DataFrame(pca.fit_transform(X))
        Y_pca.columns = ['PC1','PC2','PC3']
        Y_pca[col1] = df[col1]

        return Y_pca, explained_variance
        
    @staticmethod
    def nnc_relation(df, conf_dict, col1, col2, col3, Export=False):
        import itertools
        markers = ['x', 'o', '^']
        color = itertools.cycle(['r', 'y', 'c', 'y', 'k']) 
        groups = df[[col1, col2, col3]].groupby(col3)

        # Plot
        fig, ax = plt.subplots()
        ax.margins(0.05) 

        #print groups
        for (name, group), marker in zip(groups, itertools.cycle(markers)):
            ax.plot(group[col1], group[col2], marker='o', linestyle='', ms=4, label=name)
        ax.set_xlabel(col1)
        ax.set_ylabel(col2)
        ax.legend(numpoints=1, loc='best', title=col3)