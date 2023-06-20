"""
La empresa Grafito cuenta con un sistema de ayuda a sus usuarios en cuanto a TI con el fin de solucionar problemas relacionados con el software, hardware y otros.
La mayoría de los grupos cuentan con recursos en varios países por lo cual su procesamiento es continuo. Los tickets son creados por los usuarios en el sistema de gestión SNOW según la tabla A.
No hay restricción es su creación y son procesados por un grupo de soporte de Nivel L1. El grupo L1 cuenta con 15 recursos y en promedio resuelven la acción a tomar con ese ticket según una exponencial(7000).
El grupo L1 en un 65% de las veces se identifica un problema de software o Hardware y son asignados a un grupo especial L2 Apps-Hardware. El resto de los tickets son asignados al grupo L2-Otros.

El grupo L2 Apps-Hardware cuenta con 19 recursos que reciben los tickets y tardan U(10000,25000) en resolverlos.
El 60% se resuelve en ese tiempo y se cierra.
El 40 % de estos son identificados como mejoras por lo cual son asignados al grupo Mejora-Product Owner que trabaja de 8 a 17 y cuenta con 4 recursos. Este grupo tarda en enviar la mejora a producción según una U(26000,32000) con lo cual procede a cierrar el ticket.

El grupo L2-Otros cuenta con 8 recursos que reciben los tickets y demoran U(10000,15000) en resolverlos de los cuales:
El 55% se resuelve en ese tiempo o reidentifica como “Entrenamiento” y se procede a cerrar.
El 45% restante son relacionados con Apps y hardware y son reasignados al L2 Apps-Hardware.

-------------------------------------
        TABLA DE ARRIBOS 
-------------------------------------
Hora            Tiempo arribos
0 - 8           500 +/- 150 segundos
8 - 11          270 +/- 100 segundos
11 - 15         245 +/- 90 segundos
15 - 18         320 +/- 100 segundos
18 - 21         410 +/- 190 segundos
21 - 24         445 +/- 180 segundos

"""
import random
import simpy
import numpy as np

EMPLEADOS_NIVEL_1 = 15
EMPLEADOS_NIVEL_APPS = 10
EMPLEADOS_NIVEL_HARDWARE = 9
EMPLEADOS_NIVEL_OTROS = 8
EMPLEADOS_NIVEL_PRODUCT_OWNER = 4

MEDIA_NIVEL_UNO = 7000

MEDIA_NIVEL_APPS = 10000
DESVIO_NIVEL_APPS = 25000

MEDIA_NIVEL_HARDWARE = 10000
DESVIO_NIVEL_HARDWARE = 25000

MEDIA_NIVEL_OTROS = 10000
DESVIO_NIVEL_OTROS = 15000

MEDIA_NIVEL_PRODUCT_OWNER = 6000
DESVIO_NIVEL_PRODUCT_OWNER = 2000

TIEMPO_SIMULACION = 86400 # 24 hs

ticketsAtendidos = 0
ticketsResueltos = 0

def proximoArribo(env):
    """Distribuciones para los tiempo de arribos según horario, usando distribución normal"""
    if(env.now >= 0 and env.now < 28800 ):  t_arribos = max(60, np.random.normal(500, 150))  # 0 a 8 hs
    elif(env.now >= 28800 and env.now < 39600 ):  t_arribos = max(60, np.random.normal(270, 100))  # 8 a 11hs
    elif(env.now >= 39600 and env.now < 54000 ): t_arribos = max(60, np.random.normal(245, 90)) # 11 a 15hs
    elif(env.now >= 54000 and env.now < 64800 ): t_arribos = max(60, np.random.normal(320, 100))# 15 a 18 hs
    elif(env.now >= 64800 and env.now < 75600 ): t_arribos = max(60, np.random.normal(410, 190)) #18 a 21 hs
    elif(env.now >= 75600): t_arribos = max(60, np.random.normal(445, 180)) #21 a 24 hs
    return t_arribos

def HelpDesk(env):
    #Resource --> STORAGES
    emp_level1 = simpy.Resource(env,EMPLEADOS_NIVEL_1) 
    emp_app = simpy.Resource(env,EMPLEADOS_NIVEL_APPS)
    emp_prodOwn = simpy.Resource(env,EMPLEADOS_NIVEL_PRODUCT_OWNER) 
    emp_Harware= simpy.Resource(env,EMPLEADOS_NIVEL_HARDWARE) 
    emp_otros= simpy.Resource(env,EMPLEADOS_NIVEL_OTROS) 
    
    global ticketsAtendidos

    while (True):
        yield env.timeout(proximoArribo(env))
        print(f'nuevo arribo a las {env.now:.2f}')
        ticketsAtendidos +=1
        t = ticket(env,emp_level1, emp_app,emp_prodOwn,emp_Harware, emp_otros,ticketsAtendidos)
        env.process(t) #arribo de procesos (transacciones)    
        
def ticket(env,emp_level1, emp_app,emp_prodOwn,emp_Harware, emp_otros, i):
    """Funcion encargada de hacer el paso de los tickets a los diferentes niveles"""
    global ticketsResueltos

    print(f'ticket_{i} asignado al equipo de Nivel 1 a las {env.now:.2f}')
    with emp_level1.request() as req: 
        yield req
        print(f'ticket_{i} tomado por grupo nivel 1 a las {env.now:.2f}')
        yield env.timeout(max(60, np.random.exponential(MEDIA_NIVEL_UNO)))
        print(f'grupo de Nivel 1 terrmino de atender el ticket_{i} a las {env.now:.2f}')

    siguiente = random.choices(population=["apps","hardware","otros","productOwner","end"], weights=[0.25, 0.35, 0.25, 0.05, 0.1])[0]

    if siguiente == "apps":
        print(f'ticket_{i} asignado al equipo de Apps a las {env.now:.2f}')     
        with emp_app.request() as req: 
            yield req
            print(f'ticket_{i} tomado por equipo Apps a las {env.now:.2f}')
            yield env.timeout(max(60,np.random.uniform(MEDIA_NIVEL_APPS, DESVIO_NIVEL_APPS)))
            print(f'El equipo de Apps terrmino de atender el ticket_{i} a las {env.now:.2f}')

        siguiente = random.choices(population=["productOwner","end"], weights=[0.40, 0.60])

        if siguiente == "productOwner":
            print(f'ticket_{i} asignado a grupo Mejora-Product Owner a las {env.now:.0f}')
            with emp_prodOwn.request() as req: 
                yield req
                print(f'ticket_{i} tomado por product owner a las {env.now:.2f}')
                yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_PRODUCT_OWNER, DESVIO_NIVEL_PRODUCT_OWNER)))

    elif siguiente == "hardware":
        print(f'Ticket_{i}  asignado al equipo de Hardware a las {env.now:.0f}')
        with emp_Harware.request() as req: 
            yield req
            print(f'ticket_{i} tomado por el equipo de Hardware a las {env.now:.2f}')
            yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_HARDWARE, DESVIO_NIVEL_HARDWARE)))
            print(f'El equipo de Hardware  terrmino de atender el ticket_{i} a las {env.now:.2f}')

    elif siguiente == "otros":
        print(f'Ticket_{i} asignado al equipo de Otros a las {env.now:.0f}')
        with emp_otros.request() as req: 
            yield req
            print(f'ticket_{i} tomado por el equipo de Otros a las {env.now:.2f}')
            yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_OTROS, DESVIO_NIVEL_OTROS)))
            print(f'El equipo de Otros  terrmino de atender el ticket_{i} a las {env.now:.2f}')

    elif siguiente == "productOwner":
        print(f'ticket_{i} asignado a grupo Mejora-Product Owner a las {env.now:.0f}')
        with emp_prodOwn.request() as req: 
            yield req
            print(f'ticket_{i} tomado por product owner a las {env.now:.2f}')
            yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_PRODUCT_OWNER, DESVIO_NIVEL_PRODUCT_OWNER)))
            print(f'El product owner terrmino de atender el ticket_{i} a las {env.now:.2f}')
   
    print("**********************************************************************")
    print(f'TICKET_{i} RESUELTO A LAS {env.now:.0f}')
    print("**********************************************************************")
    ticketsResueltos+=1

   

env = simpy.Environment()#creo empleado, este es un recurso de capacidad 1 (ACA TANTO FACILITY Y STORAGE ES RECURSO)
env.process(HelpDesk(env))
env.run(until=TIEMPO_SIMULACION)
print(f"Tickets resueltos: {ticketsResueltos} ")
print(f"Tickets empezados pero sin resolver: {ticketsAtendidos-ticketsResueltos} ")

