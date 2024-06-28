from openai import OpenAI 
import os
import streamlit as st
from IPython.display import Image, display, Audio, Markdown
import base64

from streamlit_lottie import st_lottie


## Set the API key and model name
MODEL="gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-"))


IMAGE_PATH = "./data/bmi.PNG"

# Preview image for context
display(Image(IMAGE_PATH))

@st.cache_resource
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

base64_image = encode_image(IMAGE_PATH)
st.image('logo2.jpg')
st.header('BMI Analysis')
image_on = st.toggle("Inbody 보기")
on = st.toggle("Inbody 분석 보기")

if image_on : 
    st.image(IMAGE_PATH)

if on: 
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"You are a helpful health trainer. Analyze user's body based on the BMI report. Answer in only Korean. "},
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze body status in specific. Describe how user's body is changing based on the body composition history located at the left lower corner. Predict user's lifestyle based on inbody results as well.  "},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )
    description= response.choices[0].message.content
    st.write(description)
    st.download_button(
        label="분석 다운로드",
        data=description,
        file_name="inbody.txt",
        mime="text/csv",
    )

st.header('Inbody 기반 Diet Plan')
weight = st.number_input("감량 체중 목표 (Kg)", value=None)
duration = st.number_input("다이어트 기간 (days)" , value=None)


if weight !=None and duration !=None:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"You are a helpful health trainer. Help user loose {weight} kg in {duration} days. Answer in Korean only."},
            {"role": "user", "content": [
                {"type": "text", "text": f"In order to loose {weight} kg in {duration} days, make me a list of workouts and daily diet plan based on inbody results. It should include very specific workout routines and meal plans. Add some tips to successful diet at the end."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )
    answer= response.choices[0].message.content
    st.write(answer)
    st.download_button(
        label="다이어트 플랜 다운로드",
        data=answer,
        file_name="diet.txt",
        mime="text/csv",
    )