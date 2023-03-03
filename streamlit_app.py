import streamlit as st
from io import StringIO
from make import BEPUB,GPT3,ChatGPT
import os


st.title("Bilngual Book Maker")
st.write("This is a simple app to make bilingual books")
st.markdown("All glory to [@yihong0618](https://github.com/yihong0618/bilingual_book_maker)")
book_name=st.file_uploader("Upload your book",type=['epub'])
if book_name is not None:
    with open(book_name.name,"wb") as f:
        f.write(book_name.getbuffer())
col1,col2=st.columns(2)
openai_key=col1.text_input("OpenAI API Key",type="password")
model_select=col2.selectbox("Model",["ChatGPT","GPT3"])

no_limit=col1.checkbox("No Limit")
test=col2.checkbox("Test")

make_button=st.button("Make Bilingual Book")
if make_button:
    MODEL_DICT = {"GPT3": GPT3, "ChatGPT": ChatGPT}
    model = MODEL_DICT.get(model_select, "chatgpt")
    bilingual_book_name=book_name.name.split(".")[0]+"_bilingual.epub"
    if os.path.exists(bilingual_book_name) == False:
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        e = BEPUB(book_name.name, model, openai_key,my_bar)
        e.make_bilingual_book()

    with open(bilingual_book_name,"rb") as f:
        book=f.read()


    if book is not None:
        download_button=st.download_button(
            label="Download",
            data=book,
            file_name=bilingual_book_name,
        )
        # delete the file
        if download_button:
            os.remove(bilingual_book_name)
            os.remove(book_name.name)
        