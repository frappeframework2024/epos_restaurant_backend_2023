   
__version__ = '0.0.1'


import frappe
from .socket_server import start_socket_server

def boot_session(bootinfo):
    start_socket_server()