import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table

import pandas as pd

theme_color_code = "#038387" #Teal

## Component 1: Microsoft logo
microsoftlogo = dbc.Row(
    dbc.Col(
       [ html.Img(src='assets/microsoftlogo.png')]
    )
)

## Component 2. Header title
header = dbc.Row(
    [
        dbc.Col(
                [
                    html.H2(
                        "Automated Exploratory Data Analysis Tool",
                        style={'text-align':'center', "color":"white", "font-family": "Verdana; Gill Sans"}
                            )
                ],
                style ={"padding":"2% 2% 3% 1%", "background-color":theme_color_code}
               )
    ],
    style = {'text-align':'center', "padding":"2% 2% 1% 1%", "background-color":theme_color_code}
)

## Component 3. Sidebar specifications
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Automated Exploratory Data Analysis Tool", className="display-5"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Profile Data", href="/profile-data", id="profile-data-link"),
                dbc.NavLink("Descriptive Statistics", href="/descriptive-statistics", id="descriptive-statistics-link"),
                dbc.NavLink("Univariate Analysis", href="/univariate", id="univariate-link"),
                dbc.NavLink("Multivariate Analysis", href="/multivariate", id="multivariate-link"),
                dbc.NavLink("Visualize Numerical Variables", href="/numerical-visualize", id="numerical-viz-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content")

## Component 4. Data profiling layout

### 4.1. Header text
data_profiling_header_text = html.H4("1. High-level profile of data")

### 4.2. Description text
data_description = dcc.Markdown(id="data_description")

### 4.3. Slider
slider = dbc.FormGroup(
    [
        dbc.Label("Select number of rows to display from the data", html_for="slider"),
        dcc.Slider(id="slider", min=1, max=30, step=1, value=5,
                    marks = {i:i for i in range(1,31)}),
    ]
)

slider_rows = dbc.Form([slider])

### 4.4. Sample data table
table = html.Div(id="sample_table")

profile_data_layout = dbc.Col(
    [
        html.Br(),
        data_profiling_header_text,
        html.Br(),
        data_description,
        html.Br(),
        slider_rows,
        table
    ]
)

## Component 5. Descriptive statistics
descriptive_statistics_header_text = html.H4("2. Descriptive statistics of each column", id="description-header")

### 5.2. Descriptive stats of numerical variables
summary_num = html.Div(id="summary_num")

### 5.3. Descriptive stats of categorical variables
summary_cat = html.Div(id="summary_cat")

descriptive_statistics_layout = dbc.Col(
    [   
        html.Br(),
        descriptive_statistics_header_text,
        html.Br(),
        summary_num,
        summary_cat
    ]
)


## Component 6. Explore target variables
target_variable_header = html.H4("3. Explore the target variables", id="target-header")

target_dropdown = dbc.Select(id="target-dropdown")

target_distribution = dbc.Row(
        [
            dbc.Col(dcc.Graph(id='target-distribution-bar')),
            dbc.Col(dcc.Graph(id='target-distribution-pie'))
        ]
    )

target_variable_layout = dbc.Col(
    [   
        html.Br(),
        target_variable_header,
        target_dropdown,
        html.Br(),
        target_distribution
    ]
)

## Component 7. Explore numerical variables
num_variable_header = html.H4("4. Explore the numerical variables", id="numerical-header")

numerical_dropdown = dbc.Select(id="numerical-dropdown")

num_distribution = html.Div(
    [
        dbc.Row(
            dbc.Col(
                dcc.Markdown(id="normality-test"),
            align = "center"
            )
        ),
        dbc.Row(
    [
        dbc.Col(dcc.Graph(id='num-distribution-bar')),
        dbc.Col(dcc.Graph(id='num-distribution-kde'))
    ]
),
        dbc.Row(
    [
        dbc.Col(dcc.Graph(id='num-distribution-qq')),
        dbc.Col(dcc.Graph(id='num-distribution-box'))
    ]
)
    ]
)

num_variable_layout = dbc.Col(
    [   
        html.Br(),
        num_variable_header,
        numerical_dropdown,
        html.Br(),
        html.Br(),
        num_distribution
    ]
)   
    

## Component 8. Explore categorical variables
categorical_variable_header = html.H4("5. Explore the categorical variables", id="categorical-header")

categorical_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Select column", html_for="categorical-dropdown"),
                dbc.Select(id="categorical-dropdown")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Select top n values", html_for="categorical-top-n"),
                dbc.Select(id="categorical-top-n")
            ]
        )
        ]
    )

categorical_distribution = dbc.Row(
        [
            dbc.Col(dcc.Graph(id='categorical-distribution-bar')),
            dbc.Col(dcc.Graph(id='categorical-distribution-pie'))
        ]
    )

categorical_variable_layout = dbc.Col(
    [   
        html.Br(),
        categorical_variable_header,
        categorical_dropdown,
        html.Br(),
        categorical_distribution
    ]
)

univariate_layout = html.Div(
    [
        dbc.Row(target_variable_layout),
        dbc.Row(num_variable_layout),
        dbc.Row(categorical_variable_layout)
    ]
)

## Component 9. Explore Interactions Between Variables

### 9.1. Rank variables
rank_variable_header = html.H4("6. Rank variables", id="rank-header")
rank_variable_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Ref Var:", html_for="rank-ref-var"),
                dbc.Select(id="rank-ref-var")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Top Num Vars:", html_for="rank-top-num"),
                dbc.Select(id="rank-top-num")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Top Cat Vars:", html_for="rank-top-cat"),
                dbc.Select(id="rank-top-cat")
            ]
        )
        ]
    )
rank_variable_bar_num = dbc.Row(
        [
            dbc.Col(dcc.Graph(id='rank-variables-num')),
            dbc.Col(dcc.Graph(id='rank-variables-cat'))
        ]
    )


### 9.2. Interaction between categorical variables
cat_correlation_header = html.H4("7. Explore interactions between categorical variables", id="cat-corr-header")

cat_correlation_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Categorical variable 1:", html_for="cat-var-1"),
                dbc.Select(id="cat-var-1")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Categorical variable 2:", html_for="cat-var-2"),
                dbc.Select(id="cat-var-2")
            ]
        )
        ]
    )

cat_corr_heatmap = dcc.Graph(id='cat-corr-heatmap')

### 9.3. Interaction between numerical variables
num_intr_header = html.H4("8. Explore interactions between numerical variables (on sampled data)", id="intr-corr-header")

num_intr_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Numerical variable 1:", html_for="intr-var-1"),
                dbc.Select(id="intr-var-1")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Numerical variable 2:", html_for="intr-var-2"),
                dbc.Select(id="intr-var-2")
            ]
        )
        ]
    )

num_intr_scatter = dcc.Graph(id='num-intr-scatter')

### 9.4. Explore correlation matrix between numerical variables
num_correlation_header = html.H4("9. Explore correlation matrix between numerical variables", id="num-corr-header")

num_correlation_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Correlation Method:", html_for="num-var-method"),
                dbc.Select(id="num-var-method", options = [{"label":'Pearson', "value":'pearson'},
                                                    {"label":'Kendall', "value":'kendall'},
                                                    {"label":'Spearman', "value":'spearman'}],
                                                value = 'pearson')
            ]
        )
        ]
    )

num_corr_heatmap = dcc.Graph(id='num-corr-heatmap')

### 9.5. Explore interactions between numerical and categorical variables
num_cat_intr_header = html.H4("10. Explore interactions between numerical and categorical variables", id="num-cat-intr-header")

num_cat_intr_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Numerical variable:", html_for="num-cat-intr-num"),
                dbc.Select(id="num-cat-intr-num")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Categorical variable:", html_for="num-cat-intr-cat"),
                dbc.Select(id="num-cat-intr-cat")
            ]
        )
        ]
    )

num_cat_intr_plot = dcc.Graph(id='num-cat-intr-plot')


### 9.6. Explore interactions between two numerical variables and a categorical variable (on sampled data)
num_num_cat_intr_header = html.H4("11. Explore interactions between two numerical variables and a categorical variable (on sampled data)", 
                                    id="num-cat-intr-header")

num_num_cat_intr_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Numerical variable 1:", html_for="num-num-cat-intr-num-1"),
                dbc.Select(id="num-num-cat-intr-num-1")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Numerical variable 2:", html_for="num-num-cat-intr-num-2"),
                dbc.Select(id="num-num-cat-intr-num-2")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("Categorical variable (legend):", html_for="num-num-cat-intr-cat"),
                dbc.Select(id="num-num-cat-intr-cat")
            ]
        )
        ]
    )

num_num_cat_intr_plot = dcc.Graph(id='num-num-cat-intr-plot')

interactions_layout = dbc.Col(
    [   
        html.Br(),
        rank_variable_header,
        rank_variable_dropdown,
        rank_variable_bar_num,
        html.Br(),
        cat_correlation_header,
        cat_correlation_dropdown,
        cat_corr_heatmap,
        html.Br(),
        num_intr_header,
        num_intr_dropdown,
        num_intr_scatter,
        html.Br(),
        num_correlation_header,
        num_correlation_dropdown,
        num_corr_heatmap,
        html.Br(),
        num_cat_intr_header,
        num_cat_intr_dropdown,
        num_cat_intr_plot,
        html.Br(),
        num_num_cat_intr_header,
        num_num_cat_intr_dropdown,
        num_num_cat_intr_plot
    ]
)


### 10. Visualize Numerical Data by Projecting to Principal Component Spaces
num_viz_header = html.H4("12. Visualize Numerical Data by Projecting to Principal Component Spaces", 
                                    id="num-viz-header")

num_viz_3d_dropdown = dbc.Col(
            [
                dbc.Label("Categorical variable (legend):", html_for="num-viz-3d-cat"),
                dbc.Select(id="num-viz-3d-cat")
            ]
        )

num_viz_3d_plot = dcc.Graph(id='num-viz-3d-plot')

num_viz_dropdown = dbc.Row(
        [
            dbc.Col(
            [
                dbc.Label("Categorical variable (legend):", html_for="num-viz-cat"),
                dbc.Select(id="num-viz-cat")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("PC at X-axis:", html_for="num-viz-pc-x"),
                dbc.Select(id="num-viz-pc-x")
            ]
        ),
            dbc.Col(
            [
                dbc.Label("PC at Y-axis:", html_for="num-viz-pc-y"),
                dbc.Select(id="num-viz-pc-y")
            ]
        )
        ]
    )

num_viz_2d_plots = dbc.Row(
    [
        dbc.Col(dcc.Graph(id='pca-variance-bar')),
        dbc.Col(dcc.Graph(id='pca-components-2d'))
    ]
)

num_viz_layout = dbc.Col(
    [   
        html.Br(),
        num_viz_header,
        num_viz_3d_dropdown,
        num_viz_3d_plot,
        html.Br(),
        num_viz_dropdown,
        num_viz_2d_plots
    ]
)

## Bring it all together
layout = dbc.Container(
    [
        dcc.Store(id='memory-output', storage_type='memory'),
        dbc.Col(
            [
                html.Div([dcc.Location(id="url"), sidebar])
            ]
        ),
        dbc.Col(
            [
                microsoftlogo,
                header,
                content
            ], align = 'stretch'
        )
    ], 
)