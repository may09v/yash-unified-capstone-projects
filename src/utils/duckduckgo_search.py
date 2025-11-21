from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.messages import SystemMessage, HumanMessage
from langdetect import detect
import re
from dateparser import parse
import requests
import bs4

import aiohttp
import asyncio

from pathlib import Path
import sys
prompt_path = Path.cwd().parent / "src" / "prompt_engineering"
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

llm_path = Path.cwd().parent / "src" / "llm"
if str(llm_path) not in sys.path:
    sys.path.insert(0, str(llm_path))

from prompt_template import summerize_data_for_query,web_data_pre_validate_prompt
from lite_llm_client import create_chat_model

import asyncio
from fastapi.concurrency import run_in_threadpool
 
 
class DuckDuckGo:
    def __init__(self, max_results=3):
        self.wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)
 
    # --------------------------------------------------
    # 1. SEARCH NEWS
    # --------------------------------------------------
    async def search_duckduckgo(self, query: str):
        """async wrapper for duckduckgo search"""
        def _search():
            results = self.wrapper.results(
                query + " news published recently english only",
                max_results=self.wrapper.max_results,
            )
 
            english = []
            for r in results:
                try:
                    text = r.get("snippet") or r.get("body") or r.get("title", "")
                    if detect(text) == "en":
                        english.append(r)
                except:
                    continue
 
            return english[:3]
 
        return await run_in_threadpool(_search)
 
    # --------------------------------------------------
    # 2. FETCH WEB CONTENT & SUMMARIZE
    # --------------------------------------------------
    async def fetch_and_summarize(self, url: str, user_query: str):
        """fetch webpage & summarize using LLM async safe"""
 
        def _fetch():
            if not url.startswith("https"):
                return None
 
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = bs4.BeautifulSoup(res.text, "lxml")
            return soup.body.get_text(" ", strip=True) if soup.body else ""
 
        text = await run_in_threadpool(_fetch)
        if not text:
            return None
 
        # Summarization LLM
        def _summarize():
            conn = create_chat_model()
            if not conn.get("status"):
                return text[:2000]
 
            llm = conn["model"]
            system_msg = SystemMessage(content="Summarize news professionally.")
            human_msg = HumanMessage(
                content=summerize_data_for_query.format(
                    user_query=user_query,
                    data=text[:20000]
                )
            )
            return llm.invoke([system_msg, human_msg]).content
 
        return await run_in_threadpool(_summarize)
 
    async def fetch_single_url(self, session, url, user_query, llm):
       try:
           print(url)
           async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as res:
               html = await res.text()
           soup = bs4.BeautifulSoup(html, "lxml")
           text_content = soup.body.get_text(" ", strip=True) if soup.body else ""
           system_msg = SystemMessage(
               content="You are a helpful assistant specializing in news summarization."
           )
           human_msg = HumanMessage(
               content=summerize_data_for_query.format(
                   user_query=user_query,
                   data=text_content[:20000]
               )
           )
           # ASYNC call to LLM
           result = await llm.ainvoke([system_msg, human_msg])
           res= {
               "url":url,
               "summery":result.content
           }
           return res
       except Exception as e:
           res= {
               "url":url,
               "summery":None
           }
           return res
       
    async def fetch_web_data(self, urls, user_query):
        connection_status = create_chat_model()
        if not connection_status.get("status"):
           return None
        llm = connection_status["model"]
        async with aiohttp.ClientSession() as session:
           tasks = [
               self.fetch_single_url(session, url, user_query, llm)
               for url in urls
               if str(url).startswith("https")
           ]
           # Run all URLs asynchronously in parallel
           results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    # --------------------------------------------------
    # 3. MAIN FUNCTION FOR A SINGLE QUERY
    # --------------------------------------------------
    async def get_all_data_about(self, query: str):
        """
        Fully async → search → fetch → summarize
        """
        url_list = []
        for item in query:
            urls = self.search_duckduckgo(item)
            url_list.extend(urls)
        output = url_list
        return output
 
