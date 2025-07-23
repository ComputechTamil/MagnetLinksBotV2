from gtrequest import gturl
import requests
from bs4 import BeautifulSoup as bs
def adr(url)->bs:
    req=requests.get(url)
    return bs(req.text,"html.parser")
def extract_links(pages)->list:
    return [i.get("href")for i in pages]
def get_magnet_links(moviename:str,all_links=False)->list:
    moviename ="$".join(moviename.split())
    url=f"https://www-1tamilblasters-com.translate.goog/index.php?/search/&q={moviename}&search_and_or=and&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp"
    tb_page=adr(url)
    pages=tb_page.findAll("a",attrs={"data-linktype":"link"})
    pages_link=extract_links(pages)
    if not all_links:
        magnets_a = adr(pages_link[0]).findAll("a",class_="magnet-plugin")
    else:
        magnet_a = [adr(i).findAll("a",class_="magnet-plugin") for i in pages_links]
    
    magnets_links=extract_links(magnets_a)
    return magnets_links
if __name__=="__main__":
    moviename="peaky blinders"
    links=get_magnet_links(moviename)
    print(f"found:{len(links)}")
    
