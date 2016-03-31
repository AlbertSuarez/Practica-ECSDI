# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 10:47:57 2013

Webservice flask con tres entradas

 / - Responde con Hola mundo
 /pag - pagina web que enseña una pagina con numeros de 0 al 9
 /agent1 - Responde con un mensaje diferente si se recibe un GET o un POST

@author: javier
"""

from multiprocessing import Process
from flask import Flask, request, render_template
from time import sleep

app = Flask(__name__)


@app.route("/")
def hello():
    """
    El hola mundo de los servicios web
    :return:
    """
    return "Hello World!"


@app.route("/pag")
def pag():
    """
    Entrada que sirve una pagina de web que cuenta hasta 10
    :return:
    """
    return render_template('file.html', values=range(10))


@app.route("/agent1", methods=['GET', 'POST'])
def agent1():
    """
    Entrada del Servicio que responde de manera diferente a GET y POST
    :return:
    """
    if request.method == 'GET':
        return "This is Agent1"
    else:
        return "Message Received\n"


def mainloop():
    """
    Proceso concurrente haciendo sus cosas
    :return:
    """
    for i in range(10):
        print 'Este poceso es concurrente', i
        sleep(3)
    print 'y ya se acabo'


if __name__ == "__main__":
    p1 = Process(target=mainloop)
    p1.start()
    app.run()

