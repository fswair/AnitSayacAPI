from requests import get
from re import compile
from time import ctime
from bs4 import BeautifulSoup
from fastapi import FastAPI

class AnitSayac:
    """
    AnitSayac verilerini çekmek için kullanılan sınıf.
    """
    base_url = 'https://anitsayac.com/'
    def tumu(self):
        response = get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.select("a.html5lightbox")
        getid = lambda link: int(link.get("href").split("id=")[1])
        victims = [
            dict(id=getid(link), name=link.text, origin=f"{self.base_url}{link['href']}", endpoint=f"https://anitsayac.mert.uno/detay/{getid(link)}")
            for link in links
            if link['href'].startswith("details.aspx")
        ]
        
        return victims
    
    def getir(self, id: int):
        response = get("https://anitsayac.com/details.aspx?id=" + str(id))
        soup = BeautifulSoup(response.text, 'html.parser')
            
        image_source = self.base_url + soup.select_one("img").get("src")
        persons = soup.select_one("body")
            
        pattern = compile(r"</b>(.*?)<br/>")
        titles = [
                "ad", "yas", "il_ilce", "tarih", "oldurulme_sebebi",
                "tarafindan", "korunma_talebi", "oldurulme_sekli",
                "failin_durumu", "kaynak"
        ]
            
        datas = pattern.findall(str(persons))
        final_data = dict(zip(titles, map(str.strip, datas)))
        final_data["image"] = image_source
        
        return final_data


sayac = AnitSayac()

app = FastAPI()

@app.get("/")
def tumveriler():
    data = sayac.tumu()
    return dict(request_time=ctime(), length=len(data), data=data)

@app.get("/detay/{id}")
def detay(id: int):
    try: return {"status_code": 200, "data": sayac.getir(id)}
    except: return {"status_code": 404, "data": []}
