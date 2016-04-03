"""
.. module:: FlaskAgent

FlaskAgent
*************

:Description: FlaskAgent

  Simple servicio web Flask que envia y recibe mensajes con otra instancia del mismo servicio.

  Se ha de invocar desde linea de comandos por ejemplo:

  python FlaskAgent.py --host localhost --port 9000 --acomm localhost --aport 9001 --messages a b c

  donde:
   --host es la maquina donde corre el servicio (por defecto localhost)
            si se usa el host 0.0.0.0 se podra ver el servicio desde otras maquinas
   --port es el puerto de escucha del servicio
   --acomm es la maquina donde esta el servicio al que se le enviaran mensajes
   --aport es el puerto donde escucha el servicio con el que nos vamos a comunicar
   --messages es una lista de mensajes que se enviaran

  para que funcione tiene que haber otra instancia del servicio en el host y puerto indicados.

  En la red de PCs de los aularios se pueden usar los puertos de 9000-10000 para comunicarse entre
  distintos pc's, se puede averiguar el nombre de la maquina en la que estamos haciendo por ejemplo
  uname -n

:Authors: bejar
    

:Version: 

:Created on: 18/02/2015 8:28 

"""

__author__ = 'bejar'

from flask import Flask, request
import argparse
import requests
from requests import ConnectionError
from multiprocessing import Process

# Definimos los parametros de la linea de comandos
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='localhost', help="Host del agente")
parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
parser.add_argument('--acomm', help='Direccion del agente con el que comunicarse')
parser.add_argument('--aport', type=int, help='Puerto del agente con el que comunicarse')
parser.add_argument('--messages', nargs='+', default=[], help="mensajes a enviar")

app = Flask(__name__)


@app.route("/")
def isalive():
    """
    Entrada del servicio para saber si esta en funcionamiento
    :return:
    """
    return 'alive'


@app.route("/comunica")
def servicio():
    """
    Entrada del servicio que recibe los mensajes

    :return:
    """
    x = request.args['content']
    print 'recibido', x
    return x


def behavior(mess, comm):
    """
    Thread del programa que se encarga de enviar los mensajes al otro servicio

    :param mess:
    :param comm:
    :return:
    """
    # Direccion del servicio con el que nos comunicamos
    address = 'http://%s:%d/' % (comm[0], comm[1])

    # Comprobamos que el otro servicio este en marcha
    # Esto tambien se podria hacer simplemente enviando mensajes a la entrada
    # /comunica del otro servicio y esperar a que haya una respuesta
    alive = False
    while not alive:
        try:
            r = requests.get(address)
            alive = r.text == 'alive'
        except ConnectionError:
            pass

    print 'Is Alive'

    # Enviamos todos los mensajes
    for m in mess:
        print 'enviando', m
        r = requests.get(address + 'comunica', params={'content': m})
        print r.text


if __name__ == '__main__':

    # parsing de los parametros de la linea de comandos
    args = parser.parse_args()

    # Ponemos en marcha el comportamiento si se indica una direccion
    if args.acomm is not None:
        ab = Process(target=behavior, args=(args.messages, (args.acomm, args.aport)))
        ab.start()

    # Ponemos en marcha el servidor
    app.run(host=args.host, port=args.port)

    # Esperamos a que acaben los behaviors
    if args.acomm is not None:
        ab.join()

    print 'The End'
