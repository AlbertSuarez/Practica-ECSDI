"""
.. module:: Semantics3

Semantics2
*************

:Description: Semantics3

    Ejemplo de uso de la API de Semantics3 (www.semantics3.com)

    Semantics3 es un sevicio web que provee informacion de productos a traves de una API REST
    Se puede utilizar la libreria requests para hacer las queries, pero es mas sencillo utilizar la
    API python que proveen para no tener que lidiar con el sistema de autorizacion

    El codigo de la libreria esta disponible en:

    https://github.com/semantics3/semantics3-python

    es instalable via pip:

     pip install semantics3

    SEM3KEY y SEM3S son la API key y el API secret que se obtiene al darse de alta como usuario.
    La version demo permite hacer 500 queries diarias por usuario.

:Authors: bejar
    

:Version: 

:Created on: 25/02/2016 15:27 

"""


from semantics3 import Products
from AgentUtil.APIKeys import SEM3KEY, SEM3SECRET

__author__ = 'bejar'


sem3 = Products(
    api_key=SEM3KEY,
    api_secret=SEM3SECRET
)

sem3.products_field("search", "iphone")

# Run the request
results = sem3.get_products()

# View the results of the request
print results['results']