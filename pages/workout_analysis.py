import streamlit as st
import pandas as pd
import altair as alt
from streamlit_lottie import st_lottie
from openai import OpenAI 
import os
import base64

st.image('logo1.jpg')


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
MODEL="gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-"))


wdf = pd.read_csv('./data/wonnieworkout.csv')

type_filter = st.multiselect('Select Workout Types', options=list(wdf['activityType'].unique()), default=list(wdf['activityType'].unique()))
year_filter = st.multiselect('Select Year', options=list(wdf['year'].unique()), default=list(wdf['year'].unique()))


data_source = wdf['sourceName'].unique()
st.write(f'Data from {data_source[0]}')

st.dataframe(
    wdf,
    hide_index=True
)




def analyze_data(question, base64_image):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"You are a helpful health trainer. Analyze Body based on graph. The data is from user's apple watch health data. Answer in Korean. "},
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze workout pattern based on the graph.  Describe workout patterns. Predict what kind of lifestyle a person has. {question}"},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )
    description= response.choices[0].message.content
    return description 


col1, col2 = st.columns(2)

with col1:
    st.subheader('무슨 요일에 어떤 운동을 가장 많이 했을까?')
    filtered_data = wdf[wdf['activityType'].isin(type_filter) & wdf['year'].isin(year_filter)].groupby(['activityType', 'day']).size().reset_index(name='count')
    st.bar_chart(filtered_data, x="day", y="count", color="activityType") 
    desc_on1 = st.toggle("AI 분석 보기")
    st.write('일요일에 운동을 제일 많이하고 금토에는 운동을 많이 안하는 편이다 ')
    st.write('2023년도에 비해 2024년도는 매일 조금이라도 운동하려고 하는 것 같다')
    st.write('매일 걷는 것 같다')

    # if desc_on1:
    #     chart = plt.plot(filtered_data['day'], filtered_data['count'], color=filtered_data['activityType'])
    #     plt.savefig('graph1.png')
    #     base64_image = encode_image('graph1.png')
    #     desc= analyze_data('무슨 요일에 어떤 운동을 가장 많이 했을까?',base64_image)
    #     st.write(desc)


with col2:
    st.subheader('월별 어떤 운동을 자주 했을까?')
    monthly_data = wdf[wdf['activityType'].isin(type_filter) & wdf['year'].isin(year_filter)].groupby(['activityType', 'month']).size().reset_index(name='count')
    st.bar_chart(monthly_data, x="month", y="count", color="activityType") 
    st.write('여름을 좋아하는 나답게 5-8월 사이에 운동을 많이 다양하게 했다. ')
    st.write('겨울을 싫어하는 것 같고 겨울에는 거의 운동을 안한다. ')
    st.write('2024 년도에는 운동의 다양성이 줄고, core training 위주 ')

st.subheader('시간별 운동')
weekday_filter = st.multiselect('요일 선택 ', options=list(wdf['day'].unique()), default=list(wdf['day'].unique()))
filtered = wdf[wdf['activityType'].isin(type_filter) & wdf['year'].isin(year_filter)  & wdf['day'].isin(weekday_filter)]
st.scatter_chart(filtered, x="ts", y="durationInMinutes", color="activityType", size="totalEnergyBurned" ) 

st.subheader('어떤 운동이 가장 짧은 시간 안에 많은 칼로리를 태웠을까?')
cal_data = wdf[wdf['activityType'].isin(type_filter) & wdf['year'].isin(year_filter)]
cal_data["EnergyBurnedper10Minutes"] = cal_data["EnergyBurnedperMinute"] * 10
st.line_chart(cal_data, x="date", y="EnergyBurnedper10Minutes", color="activityType", use_container_width=True)


st.subheader('어떤 운동을 오래 할까?')
dur_data = wdf[wdf['activityType'].isin(type_filter) & wdf['year'].isin(year_filter)]
st.scatter_chart(dur_data, x="durationInMinutes", y="EnergyBurnedperMinute", color="activityType", size="durationInMinutes" ) 



st.subheader('온도와 습도에 따른 운동')
#HKWeatherTemperature , HKWeatherHumidity
col3, col4 = st.columns(2)

with col3:
    st.subheader('온도')
    st.scatter_chart(dur_data, x="HKWeatherTemperature", y="EnergyBurnedperMinute", color="activityType" , size="durationInMinutes") 
with col4:
    st.subheader('습도')
    st.scatter_chart(dur_data, x="HKWeatherHumidity", y="EnergyBurnedperMinute", color="activityType", size="durationInMinutes" ) 


st.subheader('운동 지역')
#HKWeatherTemperature , HKWeatherHumidity
world_data = wdf[wdf['activityType'].isin(type_filter) & wdf['year'].isin(year_filter)].groupby(['HKTimeZone','activityType']).size().reset_index(name='count')
st.dataframe(
    world_data,
    hide_index=True
)