import streamlit as st
from io import StringIO
from make import BEPUB,GPT3,ChatGPT


st.title("Biingual Book Maker")
st.write("This is a simple app to make bilingual books")
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

    e = BEPUB(book_name.name, model, openai_key)
    e.make_bilingual_book()
    with open(f"{book_name.name}_bilingual.epub","rb") as f:
        book=StringIO(f.read())
    download_button=st.download_button(
        label="Download",
        data=book,
        file_name=f"{book_name.name}_bilingual.epub",
    )
