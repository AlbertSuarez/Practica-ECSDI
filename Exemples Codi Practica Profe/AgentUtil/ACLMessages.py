# -*- coding: utf-8 -*-
"""
filename: ACLMessages

Utilidades para tratar los mensajes FIPA ACL

Created on 08/02/2014

@author: javier
"""
__author__ = 'javier'

from rdflib import Graph
import requests
from rdflib.namespace import RDF

from AgentUtil.OntoNamespaces import ACL


def build_message(gmess, perf, sender=None, receiver=None,  content=None, msgcnt= 0):
    """
    Construye un mensaje como una performativa FIPA acl
    Asume que en el grafo que se recibe esta ya el contenido y esta ligado al
    URI en el parametro contenido

    :param gmess: grafo RDF sobre el que se deja el mensaje
    :param perf: performativa del mensaje
    :param sender: URI del sender
    :param receiver: URI del receiver
    :param content: URI que liga el contenido del mensaje
    :param msgcnt: numero de mensaje
    :return:
    """
    # Añade los elementos del speech act al grafo del mensaje
    mssid = 'message-'+str(sender.__hash__()) + '-{:{fill}4d}'.format(msgcnt, fill='0')
    ms = ACL[mssid]
    gmess.bind('acl', ACL)
    gmess.add((ms, RDF.type, ACL.FipaAclMessage))
    gmess.add((ms, ACL.performative, perf))
    gmess.add((ms, ACL.sender, sender))
    if receiver is not None:
        gmess.add((ms, ACL.receiver, receiver))
    if content is not None:
        gmess.add((ms, ACL.content, content))
    return gmess


def send_message(gmess, address):
    """
    Envia un mensaje usando un request y retorna la respuesta como
    un grafo RDF
    """
    msg = gmess.serialize(format='xml')
    r = requests.get(address, params={'content': msg})

    # Procesa la respuesta y la retorna como resultado como grafo
    gr = Graph()
    gr.parse(data=r.text)

    return gr


def get_message_properties(msg):
    """
    Extrae las propiedades de un mensaje ACL como un diccionario.
    Del contenido solo saca el primer objeto al que apunta la propiedad

    Los elementos que no estan, no aparecen en el diccionario
    """
    props = {'performative': ACL.performative, 'sender': ACL.sender,
             'receiver': ACL.receiver, 'ontology': ACL.ontology,
             'conversation-id': ACL['conversation-id'],
             'in-reply-to': ACL['in-reply-to'], 'content': ACL.content}
    msgdic = {} # Diccionario donde se guardan los elementos del mensaje

    # Extraemos la parte del FipaAclMessage del mensaje
    valid = msg.value(predicate=RDF.type, object=ACL.FipaAclMessage)

    # Extraemos las propiedades del mensaje
    if valid is not None:
        for key in props:
            val = msg.value(subject=valid, predicate=props[key])
            if val is not None:
                msgdic[key] = val
    return msgdic
