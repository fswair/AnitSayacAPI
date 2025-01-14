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
            
        image_source = "http:" + soup.select_one("img").get("src")
        persons = soup.select_one("body")
            
        pattern = compile(r"</b>(.*?)<br/>")
        fields = [self.make_field(b) for b in soup.select_one("body").find_all('b')]
            
        datas = pattern.findall(str(persons))
        final_data = dict(zip(fields, map(str.strip, datas)))
        final_data["image"] = image_source
        final_data["kaynak"] = final_data["kaynak"].split('"')[1].split('"')[0]
        
        return final_data
    
    @staticmethod
    def make_field(b):
            return ''.join(c if c.strip() else '_' for c in b.text.strip() if c.isalnum() or not c.strip()).lower()\
            .replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g').replace('ü', 'u').replace('ö', 'o')


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
