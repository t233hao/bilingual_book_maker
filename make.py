import argparse
import time
from abc import abstractmethod
from copy import copy
from os import environ as env

import openai
import requests
from bs4 import BeautifulSoup as bs
from ebooklib import epub
from rich import print

NO_LIMIT = False
IS_TEST = False
LANG = "Simplified Chinese"
PROMPT = f"I want you to act as an {LANG} translator, spelling corrector and improver. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in {LANG}. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, upper level {LANG} words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations, the text is: "

class Base:
    def __init__(self, key):
        pass

    def createprompt(self, text):
        target = f"/n/n{text}"
        return PROMPT + text

    @abstractmethod
    def translate(self, text):
        pass


class GPT3(Base):
    def __init__(self, key):
        self.api_key = key
        self.api_url = "https://api.openai.com/v1/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        # TODO support more models here
        self.data = {
            "prompt": "",
            "model": "text-davinci-003",
            "max_tokens": 1024,
            "temperature": 1,
            "top_p": 1,
        }
        self.session = requests.session()

    def translate(self, text):
        print(text)
        self.data["prompt"] = self.createprompt(text)
        r = self.session.post(self.api_url, headers=self.headers, json=self.data)
        if not r.ok:
            return text
        t_text = r.json().get("choices")[0].get("text", "").strip()
        print(t_text)
        return t_text


class DeepL(Base):
    def __init__(self, session, key):
        super().__init__(session, key)

    def translate(self, text):
        return super().translate(text)


class ChatGPT(Base):
    def __init__(self, key):
        super().__init__(key)
        self.key = key
        self.message=""
    def translate(self, text):
        print(text)
        openai.api_key = self.key
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        # english prompt here to save tokens
                        "content":self.createprompt(text),
                    }
                ],
            )
            t_text = (
                completion["choices"][0]
                .get("message")
                .get("content")
                .encode("utf8")
                .decode()
            )
            if not NO_LIMIT:
                # for time limit
                time.sleep(3)
        except Exception as e:
            print(str(e), "will sleep 60 seconds")
            self.message.markdown(str(e)+"will sleep 60 seconds")
            # TIME LIMIT for open api please pay
            time.sleep(60)
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": self.createprompt(text),
                    }
                ],
            )
            t_text = (
                completion["choices"][0]
                .get("message")
                .get("content")
                .encode("utf8")
                .decode()
            )
        print(t_text)
        self.message.markdown(text+"\n"+t_text)
        # self.message.markdown(t_text)
        return t_text


class BEPUB:
    def __init__(self, epub_name, model, key, progress_bar, message):
        self.epub_name = epub_name
        self.new_epub = epub.EpubBook()
        self.translate_model = model(key)
        self.origin_book = epub.read_epub(self.epub_name)
        self.progress_bar=progress_bar
        self.message=message
        self.translate_model.message=message

    def make_bilingual_book(self):
        new_book = epub.EpubBook()
        new_book.metadata = self.origin_book.metadata
        new_book.spine = self.origin_book.spine
        new_book.toc = self.origin_book.toc
        all_items = list(self.origin_book.get_items())
        # we just translate tag p
        all_p_length = sum(
            [len(bs(i.content, "html.parser").findAll("p")) for i in all_items]
        )
        print("TODO need process bar here: " + str(all_p_length))
        self.message.markdown("TODO need process bar here: " + str(all_p_length))
        index = 0
        max_progress = 20 if IS_TEST else all_p_length
        progress=0
        for i in self.origin_book.get_items():
            if i.get_type() == 9:
                soup = bs(i.content, "html.parser")
                p_list = soup.findAll("p")
                is_test_done = IS_TEST and (index > 20)
                
                for p in p_list:
                    if not is_test_done:
                        if p.text and not p.text.isdigit():
                            new_p = copy(p)
                            # TODO banch of p to translate then combine
                            # PR welcome here
                            new_p.string = self.translate_model.translate(p.text)
                            p.insert_after(new_p)
                            index += 1
                            progress+=1
                            self.progress_bar.progress(progress/max_progress)
                            is_test_done = IS_TEST and (index > 20)
                i.content = soup.prettify().encode()
            new_book.add_item(i)
            
        name = self.epub_name.split(".")[0]
        epub.write_epub(f"{name}_bilingual.epub", new_book, {})


if __name__ == "__main__":
    MODEL_DICT = {"gpt3": GPT3, "chatgpt": ChatGPT}
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--book_name",
        dest="book_name",
        type=str,
        help="your epub book name",
    )
    parser.add_argument(
        "--openai_key",
        dest="openai_key",
        type=str,
        default="",
        help="openai api key",
    )
    parser.add_argument(
        "--no_limit",
        dest="no_limit",
        action="store_true",
        help="if you pay add it",
    )
    parser.add_argument(
        "--test",
        dest="test",
        action="store_true",
        help="if test we only translat 20 contents you can easily check",
    )
    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        type=str,
        default="chatgpt",
        choices=["chatgpt", "gpt3"],  # support DeepL later
        help="Use which model",
    )
    options = parser.parse_args()
    NO_LIMIT = options.no_limit
    IS_TEST = options.test
    OPENAI_API_KEY = options.openai_key or env.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise Exception("Need openai API key, please google how to")
    if not options.book_name.endswith(".epub"):
        raise Exception("please use epub file")
    model = MODEL_DICT.get(options.model, "chatgpt")
    e = BEPUB(options.book_name, model, OPENAI_API_KEY)
    e.make_bilingual_book()
