import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
markdown_text = "On the Economic Policy Institute's webpage \
(https://www.epi.org/publication/what-is-the-gender-pay-gap-and-is-it-real/)\
They describes the challenge of parsing through the political dialogue surrounding the gender pay gap.\
Often you'll see different metrics that people cite as evidence to support their disparate positions. \
Some argue that you need to adjust the metrics to account for other differences in gender like education level. But the \
author argues that using just these adjusted metrics can be discriminatory. They cite many statistics that reveal\
that at many levels of job prestige, women tend to make less. Pew Social Trends ( https://www.pewsocialtrends.org/2020/01/30/womens-lead-in-skills-and-education-is-helping-narrow-the-gender-wage-gap/)\
, however, says that the gap is narrowing. Wages for women have increased faster than wages for men since 1980, nevertheless\
a large gap persists\n\
The GSS is the general Social Survey which has 'studied the growing complexity of American society'(http://www.gss.norc.org/About-The-GSS) for the last 40 years. \
They track collect demographic information, but also ask participants about their opinions on different issues like what the role of people of different\
genders should be. We'll focus on this data, attempting to understand both the income and job prestige of men vs. women\
and the attitudes of people of various demographics towards man and woman's place in society. "

stats = gss_clean.groupby('sex').mean()[['income','job_prestige','socioeconomic_index', 'education']].round(2).reset_index()
table = ff.create_table(stats)
bar = gss_clean.groupby(['sex', 'male_breadwinner']).size()
bar = bar.reset_index()
bar = bar.rename({0:'Count'}, axis=1)
fig_1 = px.bar(bar, x='male_breadwinner', y='Count', color='sex',
            labels={'male_breadwinner':'Preference for a Male Breadwinner', 'Count':'Count'},
            barmode = 'group')
fig_1.update_layout(showlegend=True)
fig_1.update(layout=dict(title=dict(x=0.5)))
fig_2 = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color = 'sex', 
                 trendline = 'ols',
                 height=600, width=600,
                 labels={'job_prestige':'Job Prestige', 
                        'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig_2.update(layout=dict(title=dict(x=0.5)))
fig_3 = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Income', 'sex':''})
fig_3.update(layout=dict(title=dict(x=0.5)))
fig_3.update_layout(showlegend=False)
fig_4 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Job Prestige', 'sex':''})
fig_4.update(layout=dict(title=dict(x=0.5)))
fig_4.update_layout(showlegend=False)
gss_small = gss_clean[['income','sex','job_prestige']]
gss_small['job_prestige'] = pd.cut(gss_small['job_prestige'], [0, 17, 34, 51, 68, 85, 100],
                                   labels=['Essential','No Collar','Blue Collar','Salary/Non-Exempt','White Collar','C Suite'])
gss_small=gss_small.dropna()
fig_5 = px.box(gss_small, x='income', y = 'sex', color = 'sex',
             facet_col='job_prestige', facet_col_wrap=2,      
             labels={'income':'Income', 'sex':''})
fig_5.update(layout=dict(title=dict(x=0.5)))
fig_5.update_layout(showlegend=False)

gss_clean['education_bins'] = pd.cut(gss_clean['education'], [0, 12, 16, 17, 19, 100],
                                   labels=['High School or Less','Some College','Undergrad Degree','Masters','>Masters'])
x_cols = ['satjob','relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
group_by_cols = ['sex', 'region','education_bins']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div(  [
    html.H1("Understanding the Gender Wage Gap"),
        
    dcc.Markdown(children = markdown_text),
        
    html.H2("Metrics"),
        
    dcc.Graph(figure=table),
    
    html.H2('Agreement with various statements based on sex, region, or education'),
    
        
    html.Div([
            html.H3("x-axis feature"),
            dcc.Dropdown(id='x-axis',
                         options=[{'label': i, 'value': i} for i in x_cols],
                         value='satjob'),
            html.H3("group-by feature"),
            dcc.Dropdown(id='group_by',
                         options=[{'label': i, 'value': i} for i in group_by_cols],
                         value='sex')
        ], style={'width': '25%', 'float': 'left', 'margin-bottom':'200px'}),
        
        
        html.Div([
            dcc.Graph(id="graph")
        ], style={'width': '70%', 'float': 'right'}),
    html.H2("Income vs Job Prestige by Sex"),
    dcc.Graph(figure=fig_2),
    
        html.Div([
            
            html.H2("Income by Sex"),
            
            dcc.Graph(figure=fig_3)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Job Prestige by Sex"),
            
            dcc.Graph(figure=fig_4)
            
        ], style = {'width':'48%', 'float':'right'}),
    
        html.H2('Distribution of Job Prestige by Sex'),
        
        dcc.Graph(figure=fig_5)
    
      
    
       
    
    ])

@app.callback(Output(component_id="graph",component_property="figure"), 
             [Input(component_id='x-axis',component_property="value"),
              Input(component_id='group_by',component_property="value")])


def make_figure(x, y):
    bar = gss_clean.groupby([x, y]).size()
    bar = bar.reset_index()
    bar = bar.rename({0:'Count'}, axis=1)
    return px.bar(
        bar,
        x=x,
        y="Count", color = y, barmode = 'group'
)
if __name__ == '__main__':
    app.run_server(debug=True,
                  port = 8050, 
                  host = '0.0.0.0')
