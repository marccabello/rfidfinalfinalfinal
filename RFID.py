#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Proyecto Fin de Curso "Control de acceso" Por Marc Cabello Moreso y Guillem Sanchez Roman
#Aplicacion para analizar las entradas de autentificacion, compararlas con la base de datos y dependiendo de los permisos activar(o no) y registrarlo en los logs

"""
    ESTRUCTURA PROYECTO
- Bucle infinito
- Espera una entrado por teclado
- La guarda en una variable

- Inicia conexion a la base de datos Mysql
- Consulta el ID del usuario el cual ha introducido la tarjeta y lo almacena en variable
    - Si el usuario no existe guarda un log en la Base de datos
- Consulta si el usuario tiene permisos sobre la puerta que esta intentando acceder
    - Si el usuario no tiene permiso sobre la puerta guarda un log en la Base de datos
    - Si el usuario tiene permiso sobre la puerta:
        - Guarda un log en la base de datos
        - Se abre la puerta

"""
import datetime
import time as pause
import RPi.GPIO as GPIO
import MySQLdb

door = "11T2"

#Creamos nuestro bloque principal
def main():
    #Mientras no ocurra ningun error el proceso estara activo
    while True:
        #Leemos la siguiente entrada
        id_card = input()
        if len(id_card)  == 10:
            try:
                #Creamos la conexion con la base de datos
                cnx = MySQLdb.Connection(host='rfid.c9yye1qei7pz.eu-west-3.rds.amazonaws.com',user='rfiduser',passwd='RFIDuser2018',db='proyecto')
                cursor = cnx.cursor()
                #Consulta el ID del usuario el cual ha introducido la tarjeta y lo almacena en variable
                cursor.execute("SELECT id_user FROM users WHERE id_card = %s" % (id_card))
                #Se almacena el id_user en una variable
                id_user_array = cursor.fetchone()
                if(id_user_array):
                    id_user = id_user_array[0]
                #Si el usuario no existe se le da un valor por defecto como ID para almacenarlo en el log
                else:
                    id_user=-1

                #Consulta si el usuario tiene permiso sobre la puerta
                cursor.execute("SELECT id_door FROM permissions WHERE id_user = %s" % (id_user))
                id_door_array = cursor.fetchall()
                door_finded = False
                for i in id_door_array:
                    if(i[0] == door):
                        door_finded = True
                        break

                #Se guarda un log y se abre la puerta
                if(door_finded):
                    time = datetime.datetime.now()
                    #accedemos a la base de datos y guardamos el log
                    cursor.execute("INSERT INTO logs (date,id_user,id_door,check_status) VALUES ('%s','%s','%s','1')" % (time,id_user,door))
                    #abrimos la puerta
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(14, GPIO.OUT)
                    GPIO.output(14, True)
                    pause.sleep(5)
                    GPIO.output(14, False)
                    GPIO.cleanup()

                    cnx.commit()
                #Se guarda un log como que no se le ha dado acceso
                else:
                    time = datetime.datetime.now()
                    #accedemos a la base de datos y guardamos el log
                    cursor.execute("INSERT INTO logs (date,id_user,id_door,check_status) VALUES ('%s','%s','%s','2')" % (time,id_user,door))
                    cnx.commit()

            #En caso de error se realiza un rollback
            except:
                try:
                    cnx.rollback()
                except:
                    pass

main()
