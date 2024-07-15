import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Load the data
df = pd.read_csv(r"School_achievements.csv")

# Convert all variables except for 'score' to categorical
for col in df.columns:
    if col != 'score':
        df[col] = df[col].astype('category')

# Mapping dictionaries
shichva_mapping = {5: "שכבה ה", 8: "שכבה ח"}
subject_mapping = {'A': 'ערבית', 'E': 'אנגלית', 'H': 'עברית', 'M': 'מתמטיקה', 'S': 'מדע וטכנולוגיה'}
pikuach_mapping = {1: 'ממלכתי', 2: 'ממלכתי דתי', 3: 'חרדי'}
migzar_mapping = {1: 'יהודי', 2: 'ערבי', 4: 'דרוזי', 5: 'בדואי', 6: 'צרקסי'}
ses_mapping = {1: 'גבוה', 2: 'בינוני', 3: 'נמוך'}

# Apply mappings to the dataframe
df['shichva'] = df['shichva_x'].map(shichva_mapping)
df['subject'] = df['subject_id'].map(subject_mapping)
df['pikuach'] = df['pikuach'].map(pikuach_mapping)
df['migzar'] = df['migzar'].map(migzar_mapping)
df['Socioeconomic status'] = df['ses_mosad_cat_yh'].map(ses_mapping)

# Define a custom color palette
# color_palette = ['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF5', '#F5FF33', '#FF3380']
color_palette = px.colors.qualitative.Bold

# Streamlit app
st.markdown(
    """
    <h2 style='text-align: center; font-weight: bold;font-size: 55px;'>
        Analysis of Meitzav National Test Scores
    </h2>
    """,
    unsafe_allow_html=True
)
image_path = r"pict.png"
image = Image.open(image_path)
st.image(image, caption='מיצב ראמ"ה מערכת חינוך ישראל', use_column_width=True)

# Custom CSS to reduce space between elements and headers
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 5rem;
        padding-bottom: 1rem;
        ext-align: center;
    }
    h2 {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        font-size: 35px;
    }
    .stPlotlyChart {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h2 style='text-align: center; color: #2980b9; font-weight: bold;'>
        Meitzav grade by socioeconomic status
    </h2>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)
year_bar = col1.multiselect('Filter by Year', df['year'].unique())
layer_bar = col2.multiselect('Filter by shichva', df['shichva'].unique())

# Filter data for bar plots based on selections
filtered_df_bar = df
if year_bar:
    filtered_df_bar = filtered_df_bar[filtered_df_bar['year'].isin(year_bar)]
if layer_bar:
    filtered_df_bar = filtered_df_bar[filtered_df_bar['shichva'].isin(layer_bar)]

# Calculate general mean scores for separate graph
general_mean_scores = filtered_df_bar.groupby('Socioeconomic status')['score'].mean().reset_index()
general_mean_scores['subject'] = 'General Average'

# Calculate subject-specific mean scores
survey_group_subject_means = filtered_df_bar.groupby(['subject', 'Socioeconomic status'])['score'].mean().reset_index()

# Visualization: Scores by Survey Group and Subject (without General Average)
col3, col4 = st.columns([2, 1])

with col3:
    fig = px.bar(survey_group_subject_means, color='Socioeconomic status', y='score', x='subject', barmode='group',
                 title='Grades by subject', range_y=[400, survey_group_subject_means['score'].max() + 10],
                 color_discrete_sequence=color_palette)
    fig.update_layout(showlegend=False, height=300, bargap=0.15, margin=dict(l=0, r=0, t=22, b=0), bargroupgap=0.1)
    st.plotly_chart(fig)

with col4:
    fig = px.bar(general_mean_scores, color='Socioeconomic status', y='score', x='Socioeconomic status',
                 title='General Average', range_y=[400, general_mean_scores['score'].max() + 10],
                 color_discrete_sequence=color_palette)
    fig.update_layout(xaxis={'categoryorder': 'total descending'},
                      xaxis_title='Socioeconomic status',
                      xaxis_showticklabels=False,
                      yaxis_title='Average Score',
                      xaxis_tickangle=45, margin=dict(l=0, r=0, t=22, b=5),
                      showlegend=True, height=285, bargap=0.15, bargroupgap=0.1)
    st.plotly_chart(fig)

# Visualization 2: Effects of Sector and Supervision on Grades
st.markdown(
    """
    <h2 style='color: #2980b9; font-weight: bold;font-size: 20px;'>
        Effects of migzar and pikuach on Grades
    </h2>
    """,
    unsafe_allow_html=True
)

col3, col4 = st.columns(2)

with col3:
    sector_means = filtered_df_bar.groupby(['migzar'])['score'].mean().reset_index().sort_values(by='score', ascending=False)
    fig = px.bar(sector_means, x='migzar', y='score', color='migzar', barmode='group', title='Grades by Migzar',
                 range_y=[450, sector_means['score'].max() + 10], color_discrete_sequence=color_palette)
    fig.update_layout(height=350, bargap=0, margin=dict(l=0, r=0, t=22, b=0), bargroupgap=0)
    st.plotly_chart(fig)

with col4:
    supervision_means = filtered_df_bar.groupby(['pikuach'])['score'].mean().reset_index().sort_values(by='score', ascending=False)
    fig = px.bar(supervision_means, x='pikuach', y='score', color='pikuach', barmode='group',
                 title='Grades by pikuach', range_y=[450, supervision_means['score'].max() + 10],
                 color_discrete_sequence=color_palette)
    fig.update_layout(margin=dict(l=0, r=0, t=22, b=0), height=350)
    st.plotly_chart(fig)

# Visualization: Changes in Scores Over Time
st.markdown(
    """
    <h2 style='text-align: center; color: #2980b9; font-weight: bold;'>
        change in grades over the years
    </h2>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)
migzar_time = col1.multiselect('Select Migzar', df['migzar'].unique())
pikuach_time = col2.multiselect('Select Pikuach', df['pikuach'].unique())

# Filter data for time graphs based on selections
filtered_df_time = df
if migzar_time:
    filtered_df_time = filtered_df_time[filtered_df_time['migzar'].isin(migzar_time)]
if pikuach_time:
    filtered_df_time = filtered_df_time[filtered_df_time['pikuach'].isin(pikuach_time)]

def create_time_series_plot(df, group_by, title):
    fig = go.Figure()
    for group in df[group_by].unique():
        group_data = df[df[group_by] == group]
        fig.add_trace(go.Scatter(x=group_data['year'], y=group_data['score'], mode='lines+markers', name=str(group),
                                 hovertemplate=f'{group_by}=%{{customdata[0]}}<br>year=%{{x}}<br>score=%{{y}}',
                                 customdata=group_data[[group_by]], connectgaps=True,
                                 line=dict(color=color_palette[list(df[group_by].unique()).index(group) % len(color_palette)])))
    fig.update_layout(title=title, yaxis_title='Score', height=250, margin=dict(l=0, r=0, t=22, b=0))
    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.05, y=1,
        xanchor="left", yanchor="bottom",
        text=f"{group_by}",
        showarrow=False,
    )
    return fig

st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .element-container {
        margin-bottom: 0.5rem;
    }
    .stPlotlyChart {
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

layer_time_means = filtered_df_time.groupby(['year', 'shichva'])['score'].mean().reset_index()
fig_layer = create_time_series_plot(layer_time_means, 'shichva', 'grades over the years by Shichva')
st.plotly_chart(fig_layer)

subject_time_means = filtered_df_time.groupby(['year', 'subject'])['score'].mean().reset_index()
fig_subject = create_time_series_plot(subject_time_means, 'subject', 'grades over the years by Subject')
st.plotly_chart(fig_subject)

ses_time_means = filtered_df_time.groupby(['year', 'Socioeconomic status'])['score'].mean().reset_index()
fig_ses = create_time_series_plot(ses_time_means, 'Socioeconomic status', 'grades over the years by Socioeconomic Status (SES)')
st.plotly_chart(fig_ses)

# Comparison graphs by category
st.markdown(
    """
    <h2 style='text-align: center; color: #2980b9; font-size: 30px; font-weight: bold;'>
      Comparison of Selected Categories
    </h2>
    """,
    unsafe_allow_html=True
)

comparison_category = st.selectbox('Select Category',
                                   ['Socioeconomic status', 'migzar', 'pikuach', 'rashut', 'semel_mosad'])

# Apply selection limit conditionally based on the category
if comparison_category in ['rashut', 'semel_mosad']:
    selected_categories = st.multiselect(f'Select {comparison_category.capitalize()} for Comparison (Max 5)',
                                         df[comparison_category].unique(), max_selections=5)
else:
    selected_categories = st.multiselect(f'Select {comparison_category.capitalize()} for Comparison',
                                         df[comparison_category].unique())

if not selected_categories:
    selected_categories = df[comparison_category].unique()[:3]

if selected_categories:
    selected_categories_list = list(selected_categories)  # Convert to list
    comparison_df = df[df[comparison_category].isin(selected_categories_list)]
    general_mean = df.groupby('year')['score'].mean().reset_index()

    fig = go.Figure()
    for category in selected_categories_list:
        category_data = comparison_df[comparison_df[comparison_category] == category].groupby('year')[
            'score'].mean().reset_index()
        fig.add_trace(go.Scatter(x=category_data['year'], y=category_data['score'], mode='lines+markers',
                                 name=f'{category}',
                                 hovertemplate=f'{comparison_category}={category}<br>year=%{{x}}<br>score=%{{y}}',
                                 connectgaps=True,
                                 line=dict(color=color_palette[selected_categories_list.index(category) % len(color_palette)])))
    fig.add_trace(
        go.Scatter(x=general_mean['year'], y=general_mean['score'], mode='lines+markers', name='General Average',
                   hovertemplate='General Average<br>year=%{x}<br>score=%{y}', line=dict(dash='dash', color='black'),
                   connectgaps=True))

    fig.update_layout(title=f'Comparison of Selected {comparison_category.capitalize()}')

    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.05, y=1,
        xanchor="left", yanchor="bottom",
        text=f"{comparison_category.capitalize()}",
        showarrow=False,
        font=dict(size=12)
    )

    col5, col6 = st.columns([4, 1])
    with col5:
        chart = st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.markdown(
            """
            <h4 style='text-align: left; color: black; font-size: 15px;'>
              select filters
            </h4>
            """,
            unsafe_allow_html=True
        )
        layer_comp = st.multiselect('shichva', df['shichva'].unique())
        subject_comp = st.multiselect('Subject', df['subject'].unique())

        if layer_comp:
            comparison_df = comparison_df[comparison_df['shichva'].isin(layer_comp)]
        if subject_comp:
            comparison_df = comparison_df[comparison_df['subject'].isin(subject_comp)]

        if layer_comp or subject_comp:
            if layer_comp or subject_comp:
                fig.data = []
                for category in selected_categories_list:
                    category_data = comparison_df[comparison_df[comparison_category] == category].groupby('year')[
                        'score'].mean().reset_index()
                    fig.add_trace(go.Scatter(x=category_data['year'], y=category_data['score'], mode='lines+markers',
                                             name=f'{category}',
                                             hovertemplate=f'{comparison_category}={category}<br>year=%{{x}}<br>score=%{{y}}',
                                             connectgaps=True,
                                             line=dict(color=color_palette[selected_categories_list.index(category) % len(color_palette)])))
                fig.add_trace(go.Scatter(x=general_mean['year'], y=general_mean['score'], mode='lines+markers',
                                         name='General Average',
                                         hovertemplate='General Average<br>year=%{x}<br>score=%{y}',
                                         line=dict(dash='dash', color='black'),
                                         connectgaps=True))
                fig.update_layout(
                    title=f'Comparison of Selected {comparison_category.capitalize()}',
                    xaxis_title='Year', yaxis_title='Score')
                chart.plotly_chart(fig, use_container_width=True)

# Add custom CSS for smaller filter inscriptions and default text
st.markdown(
    """
    <style>
    .css-1cpxqw2 {
        font-size: 12px;
    }
    .stMultiSelect label {
        font-size: 14px;
    }
    .stMultiSelect div[data-baseweb="select"] > div:first-of-type {
        color: black;  /* Default text color */
        font-size: 12px;  /* Default text size */
    }
    </style>
    """,
    unsafe_allow_html=True
)
