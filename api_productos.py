import requests

class APIProducts:
    
    def __init__(self):
        self.url = "https://fakestoreapi.com/products"
        self.top_products = 12
        
    
    def get_all_products(self):
        response = requests.get(url=self.url)
        response.raise_for_status()
        if response.ok:
            return response.json()
        else:
            return []
    
    def get_limit_products(self):
        response= requests.get(url=self.url, params={'limit': self.top_products})
        response.raise_for_status()
        if response.ok:
            return response.json()
        else:
            return []

    def get_product(self, id):
        response= requests.get(url=f'{self.url}/{id}')
        response.raise_for_status()
        if response.ok:
            return response.json()
        else:
            return {}
        