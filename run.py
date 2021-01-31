import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.express as px

from urllib.parse import quote as urlquote
import flask
from flask import Flask, send_from_directory, send_file, request, session, _request_ctx_stack

import base64
import datetime
import io
import os
import string
import random
import re

import numpy as np
import scipy.stats as stats

from layout import layout as desktop_layout
from layout import profile_data_layout, descriptive_statistics_layout, univariate_layout
from layout import interactions_layout, num_viz_layout

from callbacks import *
from data import data
from utils.MultiVarAnalytics import InteractionAnalytics
from app import app, server, cache, register_before_request

app.layout = desktop_layout

from app import app

data_object = data()

df = data_object.df
conf_dict = data_object.conf_dict

@app.callback(Output("page-content", "children"), [Input("tabs", "value")])
def render_page_content(tab):
    if tab == "profile-data":
        return profile_data_layout
    elif tab == "descriptive-statistics":
        return descriptive_statistics_layout
    elif tab == "univariate":
        return univariate_layout
    elif tab == "multivariate":
        return interactions_layout
    elif tab == "numerical-visualize":
        return num_viz_layout
    
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {tab} was not recognized..."),
        ]
    )


## 2. Control number of rows in table using slider
@app.callback(
    Output('sample_table', 'children'),
    [Input('slider', 'value')]
)
def generate_sample_table(value):
    return dbc.Row(
        [
            html.P(f"Showing the top {value} rows"),
            dbc.Table.from_dataframe(df.head(value), striped=True, bordered=True, hover=True, responsive=True)
        ] 
    )

## 3. Print data column description from the data
@app.callback(
    Output('data_description', 'children'),
    [Input('slider', 'value')]
)
def generate_data_description(value):
    return f'''
        * Target variable is **{data_object.conf_dict['Target']}**
        * Numerical columns are **{", ".join(data_object.conf_dict['NumericalColumns'])}**
        * Categorical columns are **{", ".join(data_object.conf_dict['CategoricalColumns'])}**
        '''

## 4. Descriptive statistics of numerical variables
@app.callback(
    Output('summary_num', 'children'),
    [Input('description-header', 'children')]
)
def generate_stats_numerical(value):
    return dbc.Row(
        [
            html.P("Descriptive statistics of numerical variables"),
            dbc.Table.from_dataframe(data_object.desc_stats_num, striped=True, bordered=True, hover=True, responsive=True)
        ] 
    )

## 5. Descriptive statistics of categorical variables
@app.callback(
    Output('summary_cat', 'children'),
    [Input('description-header', 'children')]
)
def generate_stats_categorical(value):
    return dbc.Row(
        [
            html.P("Descriptive statistics of categorical variables"),
            dbc.Table.from_dataframe(data_object.desc_stats_cat, striped=True, bordered=True, hover=True, responsive=True)
        ] 
    )

## 6. Dropdown options for target variables
@app.callback(
    [Output('target-dropdown', 'options'),
    Output('target-dropdown', 'value')],
    [Input('target-header', 'children')]
)
def set_target_dropdown_options(value):

    if type(data_object.conf_dict['Target']) == list:
        options = [{"label":target, "value":target} for target in data_object.conf_dict['Target']]
        default_value = data_object.conf_dict['Target'][0]
    else:
        options = [{"label":target, "value":target} for target in [data_object.conf_dict['Target']]]
        default_value = data_object.conf_dict['Target']

    return options, default_value

## 7. Bar and pie plots of target variable distribution
@app.callback(
    [Output('target-distribution-bar', 'figure'),
    Output('target-distribution-pie', 'figure')],
    [Input('target-dropdown', 'value')]
)
def generate_target_distribution(value):

    template = "plotly_white"
    
    eng_df = data_object.target_distribution(value)

    barplot = px.bar(eng_df, x='index', y=value, labels= {'index': value, value:'Frequency'},template=template)
    pieplot = px.pie(eng_df, values=value, names='index', template=template)

    return barplot, pieplot

## 8. Dropdown options for numerical variables
@app.callback(
    [Output('numerical-dropdown', 'options'),
    Output('numerical-dropdown', 'value')],
    [Input('numerical-header', 'children')]
)
def set_numerical_dropdown_options(value):

    if type(data_object.conf_dict['NumericalColumns']) == list:
        options = [{"label":var, "value":var} for var in data_object.conf_dict['NumericalColumns']]
        default_value = data_object.conf_dict['NumericalColumns'][0]
    else:
        options = [{"label":var, "value":var} for var in [data_object.conf_dict['NumericalColumns']]]
        default_value = data_object.conf_dict['NumericalColumns']

    return options, default_value


## 9. Numerical variable distribution
@app.callback(
    [Output('normality-test', 'children'),
    Output('num-distribution-bar', 'figure'),
    Output('num-distribution-kde', 'figure'),
    Output('num-distribution-qq', 'figure'),
    Output('num-distribution-box', 'figure')],
    [Input('numerical-dropdown', 'value')]
)
def generate_numerical_distribution(value):

    template = "plotly_white"

    status, color, p_val = data.shapiro_test(df[value])
    normality_text = f"Normality test for {value} {status} (p_value = {p_val})"

    histogram = px.histogram(df, x=value, marginal="box", template=template, title=f"Histogram of {value}")

    hist_data = [df[value]]
    group_labels = ['distplot'] # name of the dataset
    kdeplot = ff.create_distplot(hist_data, group_labels)
    kdeplot.update_layout(template=template, title=f"KDE plot of {value}")

    qq=stats.probplot(df[value])
    x = np.array([qq[0][0][0], qq[0][0][-1]])

    qqplot = go.Figure()
    qqplot.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers')
    qqplot.add_scatter(x=x, y=qq[1][1] + qq[1][0]*x, mode='lines')
    qqplot.layout.update(showlegend=False)
    qqplot.update_layout(template=template, title=f"QQ plot to check normality of {value}")

    boxplot = px.box(df, y=value, template=template, title=f"Boxplot for distribution of {value}")

    return normality_text, histogram, kdeplot, qqplot, boxplot

## 10. Dropdown options for categorical variables
@app.callback(
    [Output('categorical-dropdown', 'options'),
    Output('categorical-dropdown', 'value')],
    [Input('categorical-header', 'children')]
)
def set_categorical_dropdown_options(value):

    if type(data_object.conf_dict['CategoricalColumns']) == list:
        options = [{"label":target, "value":target} for target in data_object.conf_dict['CategoricalColumns']]
        default = data_object.conf_dict['CategoricalColumns'][0]
    else:
        options = [{"label":target, "value":target} for target in [data_object.conf_dict['CategoricalColumns']]]
        default = data_object.conf_dict['CategoricalColumns']
    return options, default

## 11. Dropdown options for categorical variables selection of top n variables
@app.callback(
    Output('categorical-top-n', 'options'),
    [Input('categorical-dropdown', 'value')]
)
def set_categorical_topn_options(value):
    options = [{"label":target, "value":target} for target in range(1, df[value].nunique() + 1)]
    return options

## 12. Distribution of categorical variables
@app.callback(
    [Output('categorical-distribution-bar', 'figure'),
    Output('categorical-distribution-pie', 'figure')],
    [Input('categorical-dropdown', 'value'),
    Input('categorical-top-n', 'value')]
)
def generate_categorical_distribution(value1, value2):

    template = "plotly_white"

    if value2:
        eng_df = data_object.target_distribution(value1).iloc[:int(value2),:]
    else:
        eng_df = data_object.target_distribution(value1)

    barplot = px.bar(eng_df, x='index', y=value1, labels= {'index': value1, value1:'Frequency'}, 
                    template=template, title = f"Bar plot for distribution of {value1}")
    pieplot = px.pie(eng_df, values=value1, names='index',template=template,
                     title = f"Pie chart for distribution of {value1}")

    return barplot, pieplot

## 13. Dropdown options for rank variables ref variables
@app.callback(
    [Output('rank-ref-var', 'options'),
    Output('rank-ref-var', 'value')],
    [Input('rank-header', 'children')]
)
def set_rank_refvar_options(value):
    options = [{"label":target, "value":target} for target in data_object.conf_dict['CategoricalColumns'] +\
                                     data_object.conf_dict['NumericalColumns']]
    return options, (data_object.conf_dict['CategoricalColumns'] + data_object.conf_dict['NumericalColumns'])[0]

## 14. Dropdown options for rank variables top num (both num and cat)
@app.callback(
    [Output('rank-top-num', 'options'),
    Output('rank-top-cat', 'options'),
    Output('rank-top-num', 'value'),
    Output('rank-top-cat', 'value')],
    [Input('rank-ref-var', 'value')]
)
def set_rank_topnum_options(value):
    options_topnum = [{"label":target, "value":target} for target in \
                range(1, len([var for var in data_object.conf_dict['NumericalColumns'] if var != value]) + 1)]

    options_topcat = [{"label":target, "value":target} for target in \
               range(1, len([var for var in data_object.conf_dict['CategoricalColumns'] if var != value]) + 1)]

    default_num_value = len([var for var in data_object.conf_dict['NumericalColumns'] if var != value])
    default_cat_value = len([var for var in data_object.conf_dict['CategoricalColumns'] if var != value])

    return options_topnum, options_topcat, default_num_value, default_cat_value

## 15. Rank variable correlations
@app.callback(
    [Output('rank-variables-num', 'figure'),
    Output('rank-variables-cat', 'figure')],
    [Input('rank-ref-var', 'value'),
    Input('rank-top-num', 'value'),
    Input('rank-top-cat', 'value')]
)
def generate_rank_correlations(refvar, topnum, topcat):

    template = "plotly_white"

    corr_num, metric_num, corr_cat, metric_cat = \
            InteractionAnalytics.rank_associations(data_object.df, data_object.conf_dict, refvar, topnum, topcat)

    bar_num = px.bar(corr_num, x='Variable', y='Correlation', labels= {'Correlation':f'Correlation ({metric_num})'}, 
                    template=template, title = f"Top {topnum} associated numerical variables")

    bar_cat = px.bar(corr_cat, x='Variable', y='Correlation', labels= {'Correlation':f'Correlation ({metric_cat})'}, 
                    template=template, title = f"Top {topcat} associated numerical variables")

    return bar_num, bar_cat

## 16. Dropdown options for categorical correlations
@app.callback(
    [Output('cat-var-1', 'options'),
    Output('cat-var-2', 'options'),
    Output('cat-var-1', 'value'),
    Output('cat-var-2', 'value')],
    [Input('cat-corr-header', 'value')]
)
def set_cat_corr_options(value):
    options = [{"label":var, "value":var} for var in data_object.conf_dict['CategoricalColumns']]
    default_value_1 = data_object.conf_dict['CategoricalColumns'][0]
    default_value_2 = data_object.conf_dict['CategoricalColumns'][-1]
    return options, options, default_value_1, default_value_2

## 17. Categorical correlation heatmap
@app.callback(
    Output('cat-corr-heatmap', 'figure'),
    [Input('cat-var-1', 'value'),
    Input('cat-var-2', 'value')]
)
def generate_cat_correlations(cat_var_1, cat_var_2):

    template = "plotly_white"

    corr_df = InteractionAnalytics.categorical_relations(data_object.df, cat_var_1, cat_var_2)
    heatmap = px.imshow(corr_df, template=template, labels=dict(color="Co-occurence Frequency"),
                title = f'{cat_var_1} vs {cat_var_2}')

    return heatmap

## 18. Dropdown options for numerical correlations
@app.callback(
    [Output('intr-var-1', 'options'),
    Output('intr-var-2', 'options'),
    Output('intr-var-1', 'value'),
    Output('intr-var-2', 'value')],
    [Input('intr-corr-header', 'value')]
)
def set_num_corr_options(value):
    options = [{"label":var, "value":var} for var in data_object.conf_dict['NumericalColumns']]
    default_value_1 = data_object.conf_dict['NumericalColumns'][0]
    default_value_2 = data_object.conf_dict['NumericalColumns'][-1]
    return options, options, default_value_1, default_value_2

## 19. Numerical correlation scatter and line plots
@app.callback(
    Output('num-intr-scatter', 'figure'),
    [Input('intr-var-1', 'value'),
    Input('intr-var-2', 'value')]
)
def generate_num_interactions(num_var_1, num_var_2):

    template = "plotly_white"

    lowess, ols, corr = InteractionAnalytics.numerical_relations(data_object.df, num_var_1, num_var_2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_object.df[num_var_2], y=data_object.df[num_var_1],
                        mode='markers',
                        name='Data Points'))

    fig.add_trace(go.Scatter(x=lowess['x'], y=lowess['lowess'],
                        mode='lines',
                        name='Lowess'))

    fig.add_trace(go.Scatter(x=ols['x'], y=ols['ols'],
                        mode='lines',
                        name='OLS'))

    fig.update_layout(
        title=f"{num_var_1} vs {num_var_2}. Correlation={corr}",
        xaxis_title=num_var_2,
        yaxis_title=num_var_1,
        template=template
        )

    return fig

## 20. Numerical correlation heatmap
@app.callback(
    Output('num-corr-heatmap', 'figure'),
    [Input('num-var-method', 'value')]
)
def generate_num_correlations(method):

    template = "plotly_white"

    corr_df = InteractionAnalytics.numerical_correlation(data_object.df, data_object.conf_dict, method)
    heatmap = px.imshow(corr_df, template=template, labels=dict(color="Corelation"),
                title = f'{method} correlation among numerical variables')

    return heatmap

## 21. Dropdown options for intereaction between numerical and categorical variables
@app.callback(
    [Output('num-cat-intr-num', 'options'),
    Output('num-cat-intr-cat', 'options'),
    Output('num-cat-intr-num', 'value'),
    Output('num-cat-intr-cat', 'value')],
    [Input('num-cat-intr-header', 'value')]
)
def set_num_corr_options(value):
    options_num = [{"label":var, "value":var} for var in data_object.conf_dict['NumericalColumns']]
    options_cat = [{"label":var, "value":var} for var in data_object.conf_dict['CategoricalColumns']]

    default_value_num = data_object.conf_dict['NumericalColumns'][0]
    default_value_cat = data_object.conf_dict['CategoricalColumns'][0]

    return options_num, options_cat, default_value_num, default_value_cat

## 22. Numerical, categorical interaction boxplot
@app.callback(
    Output('num-cat-intr-plot', 'figure'),
    [Input('num-cat-intr-num', 'value'),
    Input('num-cat-intr-cat', 'value')]
)
def generate_num_cat_interactions(num_var, cat_var):

    template = "plotly_white"

    status, p_val = InteractionAnalytics.nc_relation(data_object.df, data_object.conf_dict, num_var, cat_var)
    boxplot = px.box(data_object.df, y=num_var, x=cat_var, template=template, 
            title=f"Boxplot for distribution of {num_var} by {cat_var} \n ho {status} (p-value = {p_val})")

    return boxplot

## 23. Dropdown options for interaction between two numerical and one categorical variable
@app.callback(
    [Output('num-num-cat-intr-num-1', 'options'),
    Output('num-num-cat-intr-num-2', 'options'),
    Output('num-num-cat-intr-cat', 'options'),
    Output('num-num-cat-intr-num-1', 'value'),
    Output('num-num-cat-intr-num-2', 'value'),
    Output('num-num-cat-intr-cat', 'value')],
    [Input('num-cat-intr-header', 'value')]
)
def set_num_num_cat_options(value):
    options_num = [{"label":var, "value":var} for var in data_object.conf_dict['NumericalColumns']]
    options_cat = [{"label":var, "value":var} for var in data_object.conf_dict['CategoricalColumns']]

    default_value_num_1 = data_object.conf_dict['NumericalColumns'][0]
    default_value_num_2 = data_object.conf_dict['NumericalColumns'][-1]
    default_value_cat = data_object.conf_dict['CategoricalColumns'][0]

    return options_num, options_num, options_cat, default_value_num_1, default_value_num_2, default_value_cat

## 24. Numerical, numerical, categorical interaction scatterplot
@app.callback(
    Output('num-num-cat-intr-plot', 'figure'),
    [Input('num-num-cat-intr-num-1', 'value'),
    Input('num-num-cat-intr-num-2', 'value'),
    Input('num-num-cat-intr-cat', 'value')]
)
def generate_num_cat_interactions(num_var_1, num_var_2, cat_var):

    template = "plotly_white"
    scatterplot = px.scatter(data_object.df, x=num_var_2, y=num_var_1, color=cat_var, template=template)

    return scatterplot

## 25. Dropdown options for visualizing numerical variables dropdown
@app.callback(
    [Output('num-viz-3d-cat', 'options'),
    Output('num-viz-cat', 'options'),
    Output('num-viz-pc-x', 'options'),
    Output('num-viz-pc-y', 'options'),
    Output('num-viz-3d-cat', 'value'),
    Output('num-viz-cat', 'value'),
    Output('num-viz-pc-x', 'value'),
    Output('num-viz-pc-y', 'value')],
    [Input('num-viz-header', 'value')]
)
def set_num_viz_dropdown_options(value):
    options_cat = [{"label":var, "value":var} for var in data_object.conf_dict['CategoricalColumns']]
    default_value_cat = data_object.conf_dict['CategoricalColumns'][0]

    pc_dropdown_options = [{"label":var, "value":var} for var in \
                    range(1, len(data_object.conf_dict['NumericalColumns']) + 1)]

    pc_dropdown_default_1 = 1
    pc_dropdown_default_2 = len(data_object.conf_dict['NumericalColumns'])

    return options_cat, options_cat, pc_dropdown_options, pc_dropdown_options, default_value_cat, default_value_cat, pc_dropdown_default_1, pc_dropdown_default_2

## 26. 3D plot for visualizing principal components
@app.callback(
    [Output('num-viz-3d-plot', 'figure'),
    Output('pca-variance-bar', 'figure'),
    Output('pca-components-2d', 'figure')],
    [Input('num-viz-3d-cat', 'value'),
    Input('num-viz-cat', 'value'),
    Input('num-viz-pc-x', 'value'),
    Input('num-viz-pc-y', 'value')]
)
def generate_3d_pca(cat_var_3d, cat_var_2d, pc_x, pc_y):

    template = "plotly_white"
    pc_df, explained_variance = InteractionAnalytics.pca_3d(data_object.df, data_object.conf_dict, cat_var_3d, int(pc_x), int(pc_y))
    pc_df_2d, _ = InteractionAnalytics.pca_3d(data_object.df, data_object.conf_dict, cat_var_2d, int(pc_x), int(pc_y))


    plot_3d = px.scatter_3d(pc_df, x='PC1', y='PC2', z='PC3', color=cat_var_3d, template=template)

    plot_variance = px.bar(explained_variance, x='Component', y='Variance', template=template)

    plot_2d_pca = px.scatter(pc_df_2d, x='PC'+str(pc_x), y='PC'+str(pc_y), color=cat_var_2d, template=template)

    return plot_3d, plot_variance, plot_2d_pca


if __name__ == '__main__':
    # app.server.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    app.server.run(debug = True)