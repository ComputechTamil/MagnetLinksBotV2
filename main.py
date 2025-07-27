import aiohttp
import asyncio
from re import sub
from bs4 import BeautifulSoup as bs
from urllib.parse import unquote
from async_lru import alru_cache
import time
def Soup(url)->bs:
    req=requests.get(url)
    return bs(req.text,"html.parser")
async def fetch(session,url):
    async with session.get(url) as response:
        return await response.text()
    
def extract_links(pages,text=False):
    return [i.get("href")for i in pages]
def clean_magnet_link(string):
    string=unquote(string)
    string="".join(string.rsplit("-+")[1:-1])
    string=string.replace("+"," ").replace("-"," ")
    string=sub(r"\s+"," ",string)
    return string
def linkswithtext(lst)->dict:
    return [(clean_magnet_link(i.split("&")[1][3:]),i) for i in lst]
@alru_cache(maxsize=None)
async def get_magnet_links(moviename:str)->dict:
    moviename ="$".join(moviename.split())
    url=f"https://www-1tamilblasters-com.translate.goog/index.php?/search/&q={moviename}&search_and_or=and&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp"
    async with aiohttp.ClientSession() as session:
        html=await fetch(session,url)
        tb_page=bs(html,"html.parser")
        pages=tb_page.find_all("a",attrs={"data-linktype":"link"})
        pages_link=extract_links(pages)
        magnets_a=[]
        if not pages_link:
            return {}
        all_pages=await asyncio.gather(*[fetch(session,page) for page in pages_link])
        for page in all_pages:
            soup=bs(page,"html.parser")
            magnets_a.extend(soup.find_all("a",class_="magnet-plugin"))
        magnets_links=linkswithtext(extract_links(magnets_a))
        return magnets_links
if __name__=="__main__":
    start=time.perf_counter()
    moviename="peaky blinders" 
    links=asyncio.run(get_magnet_links(moviename))
    print(f"found:{len(links)}")
    print(time.perf_counter()-start)
    
