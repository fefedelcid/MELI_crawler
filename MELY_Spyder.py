from bs4 import BeautifulSoup
import requests
import pandas as pd

class Spider():
    valid_attrs = [
        'promotion-item__price',        # Precio actual
        'promotion-item__discount',     # Descuento (opcional)
        'promotion-item__installments', # Cuotas (opcional)
        'promotion-item__shipping',     # Envío gratis (opcional)
        'full-icon',                    # Envío full (opcional)
        'promotion-item__title',        # Título del anuncio
        'promotion-item__seller'        # Vendedor (opcional)
    ]
    
    
    def __init__(self, max_deep=1):
        self.page = 1
        self.max_deep = max_deep
        self.soup = self.get_soup()
        self.df = pd.DataFrame()
        
    
    def get_next_page(self):
        if self.page > self.max_deep:
            return None
        url = f'https://www.mercadolibre.com.ar/ofertas?page={self.page}'
        self.page += 1
        return requests.get(url)
    
    
    def get_soup(self):
        html = self.get_next_page()
        if html.status_code == 200:
            return BeautifulSoup(html.text, 'html.parser')
        else:
            print(html.status_code)
    
    
    def run(self):
        offers = self.soup.find_all('div', {'class':'promotion-item__description'})
        
        for item in offers:
            data = self.check_tags(item)
            new_data = {}
            
            for item in data:
                value = item.text
                key = item['class'][0].replace('promotion-item__', '')

                # Excepciones
                if item['class'][0] == 'full-icon':
                    key, value = 'full_shipping', True
                elif item['class'][0] == 'promotion-item__seller':
                    value = value[4:]

                new_data[key] = value
            
            self.df = self.df.append(self.check_data(new_data), ignore_index=True)
        
        self.soup = self.get_soup()
        if self.soup != None:
            self.run()
        else:
            print('Maximum depth reached')
            return self.df
            
    def check_data(self, data):
        for attr in self.valid_attrs:
            if attr not in data:
                data[attr] = None
        
        return data
    
    
    def check_tags(self, item):
        # Retorna una lista con valores válidos para el dataset
        result = []
        for tag in item.find_all():
            if tag.has_attr('class') and tag.attrs['class'][0] in self.valid_attrs:
                result.append(tag)
        return result


if __name__=='__main__':
    spidy = Spider()
    df = spidy.run()