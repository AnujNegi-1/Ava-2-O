from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import folium
from geopy.geocoders import Nominatim
from PIL import Image

# Configure Gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Speak function (text to speech)
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Voice recognition (speech to text)
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        st.success(f"You said: {query}")
        return query
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Gemini response
def my_output(query):
    response = model.generate_content(query)
    return response.text

# Search locations
def search_locations(location_name):
    try:
        geolocator = Nominatim(user_agent="ava-map-bot")
        return geolocator.geocode(location_name, exactly_one=False, limit=50)
    except Exception as e:
        st.error(f"Location service failed: {e}")
        return None

# Create map with Satellite view option
def create_map_from_coords(latitude, longitude, place_name, use_satellite=False):
    tile_type = 'Esri Satellite' if use_satellite else 'OpenStreetMap'
    m = folium.Map(location=[latitude, longitude], zoom_start=14, tiles=tile_type)
    folium.Marker([latitude, longitude], popup=place_name).add_to(m)
    return m._repr_html_()

# Streamlit UI
st.set_page_config(page_title="AVA - Smart Assistant")
st.title("🤖 Ava 2.O")

# Input Text
input_text = st.text_input("Ask Ava anything...", key="input")
submit = st.button("Submit")

# Voice Input Button
if st.button("🎙️ Speak"):
    voice_query = voice_input()
    if voice_query:
        input_text = voice_query
        response = my_output(input_text)
        st.subheader("Response:")
        st.write(response)
        speak_text(response)

# Process Text Input
if submit and input_text:
    response = my_output(input_text)
    st.subheader("Response:")
    st.write(response)

# Upload Image
st.subheader("📤 Upload an Image")
uploaded_img = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
if uploaded_img:
    image = Image.open(uploaded_img)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Map Integration
st.subheader("🗺️ Find Location on Map")
location_query = st.text_input("Enter a location (e.g., Jodhpur, Delhi)")


if st.button("Search Location"):
    if not location_query.strip():
        st.warning("Please enter a location to search.")
    else:
        results = search_locations(location_query)
        if results:
            place_options = [f"{loc.address} ({round(loc.latitude, 4)}, {round(loc.longitude, 4)})" for loc in results]
            selected_place = st.selectbox("Select a location from search results:", place_options)

            selected_index = place_options.index(selected_place)
            chosen_location = results[selected_index]

            map_html = create_map_from_coords(
                chosen_location.latitude,
                chosen_location.longitude,
                chosen_location.address,
            )
            st.components.v1.html(map_html, height=500)
        else:
            st.error("No matching location found.")

# Removed repeated text inputs and duplicate header