import streamlit as st
from io import StringIO
from make import BEPUB,GPT3,ChatGPT
import os


st.title("Bilingual Book Maker")
st.write("使用 GPT-3 或 ChatGPT 將原文電子書轉換成原文與簡體中文對照的電子書")
st.markdown("感謝 [@yihong0618](https://github.com/yihong0618/bilingual_book_maker)")
st.markdown("關於這個工具: [使用教學與 streamlit 的原始碼相關資訊](https://softnshare.com/bilingual_book_maker-streamlit/)")
st.markdown("軟體變更紀錄: [請參考這個網頁](https://softnshare.com/bilingual-book-maker-changelog/)")
book_name=st.file_uploader("Upload your book",type=['epub'])
col1,col2=st.columns(2)
openai_key=col1.text_input("OpenAI API Key",type="password")
model_select=col2.selectbox("Model",["ChatGPT","GPT3"])

no_limit=col1.checkbox("No Limit")
test=col2.checkbox("Test")

make_button=st.button("Make Bilingual Book")

st.session_state["book"]=None
# 如果tmp文件夹不存在，则创建
path="tmp"
if "Translate Success" not in st.session_state:
    st.session_state["Translate Success"] = False

if os.path.exists(path) == False:
    os.mkdir(path)
if book_name is not None:
    st.session_state["original_book_name"]=os.path.join(path,book_name.name)
    with open(st.session_state["original_book_name"],"wb") as f:
        f.write(book_name.getbuffer())

if make_button:
    MODEL_DICT = {"GPT3": GPT3, "ChatGPT": ChatGPT}
    model = MODEL_DICT.get(model_select, "chatgpt")
    st.session_state["bilingual_book_name"]=st.session_state["original_book_name"].split(".")[0]+"_bilingual.epub"
    if os.path.exists(st.session_state["bilingual_book_name"]) == False:
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        translating=st.markdown("Translating...")
        message = st.markdown(" ")


        e = BEPUB(st.session_state["original_book_name"], model, openai_key,my_bar,message)
        e.make_bilingual_book()
        my_bar.progress(100)
        translating.markdown("Done")
        message.markdown(" ")
        
    with open(st.session_state["bilingual_book_name"],"rb") as f:
        st.session_state["book"]=f.read()
    st.session_state["Translate Success"]=True

# delete the file
if st.session_state["Translate Success"]==True:
    try:
        os.remove(st.session_state["bilingual_book_name"])
        os.remove(st.session_state["original_book_name"])
        # 删除path目录下所有文件
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
    except:
        pass 

if st.session_state["Translate Success"]==True and st.session_state["book"] is not None:
    download_button=st.download_button(
        label="Download",
        data=st.session_state["book"],
        file_name=book_name.name.split(".")[0]+"_bilingual.epub",
    ) 
        
