import streamlit as st
import requests

st.title('URL Shortener')

long_url = st.text_input('Enter the url you want to shorten')

if st.button('Shorten'):
    try:
        response  = requests.post('http://backend:8000/shorten', json={'long_url': long_url})
        if response.status_code == 200:
            data = response.json()
            short_url = f"{data['short_url']}"
            st.success("URL shortened successfully!")
            st.markdown(f"[{short_url}]({short_url})")
            st.code(short_url)
        else:
            error = response.json()
            st.error(error['detail'])
    except Exception as e:
        st.write(e)
