import random
import simpy
import numpy as np
import time
import statistics
import matplotlib.pyplot as plt

EMPLEADOS_NIVEL_1 = 15
EMPLEADOS_NIVEL_APPS = 10
EMPLEADOS_NIVEL_HARDWARE = 9
EMPLEADOS_NIVEL_OTROS = 8
EMPLEADOS_NIVEL_PRODUCT_OWNER = 4

LAMDA_NIVEL_UNO = 1/60

MEDIA_NIVEL_APPS = 10000
DESVIO_NIVEL_APPS = 25000

MEDIA_NIVEL_HARDWARE = 10000
DESVIO_NIVEL_HARDWARE = 25000

MEDIA_NIVEL_OTROS = 10000
DESVIO_NIVEL_OTROS = 15000

MEDIA_NIVEL_PRODUCT_OWNER = 6000
DESVIO_NIVEL_PRODUCT_OWNER = 2000

TIEMPO_SIMULACION = 86400 # 24 hs

wait_times = list()
ticketsResueltos = list()
ticketsArribados =list()


def distribucionArribos(env):
    """Distribuciones para los tiempo de arribos según horario, usando distribución normal"""
    return max(60, np.random.exponential(1/30))

def Arrivals(env):
    #Resource --> STORAGES
    emp_level1 = simpy.Resource(env,EMPLEADOS_NIVEL_1) 
    emp_app = simpy.Resource(env,EMPLEADOS_NIVEL_APPS)
    emp_prodOwn = simpy.Resource(env,EMPLEADOS_NIVEL_PRODUCT_OWNER) 
    emp_Harware= simpy.Resource(env,EMPLEADOS_NIVEL_HARDWARE) 
    emp_otros= simpy.Resource(env,EMPLEADOS_NIVEL_OTROS) 
    
    global ticketsArribados

    while (True):
        yield env.timeout(distribucionArribos(env))
        print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} : Arribo numero {len(ticketsArribados)+1}')
        ticket = Ticket(f"Ticket_{len(ticketsArribados)+1}",env.now)
        ticketsArribados.append(ticket)
        t = HelpDesk(env,emp_level1, emp_app,emp_prodOwn,emp_Harware, emp_otros,ticket)
        env.process(t) #arribo de procesos (transacciones)    
        
class Ticket:
    """Class that represents a ticket"""
    def __init__(self, descripcion, arrival_time):
        self.descripcion = descripcion
        self.arrival_time = arrival_time
        self.wait_time = {
            'Level_One': 0,
            'Level_Apps': 0,
            'Level_Hardware': 0,
            'Level_Others': 0,
            'Level_ProductOwner': 0,
        }

    def sum_waiting_times(self, ):
        return sum(self.wait_time[x] for x in self.wait_time)
        
    def set_wait_time(self, level, waitingTime):
        self.wait_time[level] = waitingTime


def HelpDesk(env,emp_level1, emp_app,emp_prodOwn,emp_Harware, emp_otros, ticket):
    """Funcion encargada de hacer el paso de los tickets a los diferentes niveles"""
 
    print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion} : Asignado a equipo de Nivel 1')
    
    with emp_level1.request() as req: 
        yield req
        yield env.timeout(max(60, np.random.exponential(LAMDA_NIVEL_UNO)))
        print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion} : finalizo Nivel 1')
        ticket.set_wait_time('Level_One', env.now - ticket.arrival_time)

    siguiente = random.choices(population=["apps","hardware","otros","productOwner","end"], weights=[0.25, 0.35, 0.25, 0.05, 0.1])[0]

    if siguiente == "apps":
        with emp_app.request() as req: 
            yield req
            yield env.timeout(max(60,np.random.uniform(MEDIA_NIVEL_APPS, DESVIO_NIVEL_APPS)))
            print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion} : finalizo nivel Apps')
            ticket.set_wait_time('Level_Apps', env.now - ticket.sum_waiting_times())

        siguiente = random.choices(population=["productOwner","end"], weights=[0.40, 0.60])

        if siguiente == "productOwner":
            if env.now < 28800: # antes de las 8 hs no lo atienden
                yield env.timeout(28800 - env.now)
            if env.now > 61200: # despues de las 17 hs no lo atienden
                yield env.timeout(86400 - env.now) # termina el dia y no lo atienden

            with emp_prodOwn.request() as req: 
                yield req
                yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_PRODUCT_OWNER, DESVIO_NIVEL_PRODUCT_OWNER)))
                print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion} : finalizo nivel Product Owner')
                ticket.set_wait_time('Level_ProductOwner', env.now - ticket.sum_waiting_times())

    elif siguiente == "hardware":
        with emp_Harware.request() as req: 
            yield req
            yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_HARDWARE, DESVIO_NIVEL_HARDWARE)))
            print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion}: finalizo nivel Hardware')
            ticket.set_wait_time('Level_Hardware', env.now - ticket.sum_waiting_times())

    elif siguiente == "otros":
        with emp_otros.request() as req: 
            yield req
            yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_OTROS, DESVIO_NIVEL_OTROS)))
            print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion}: finalizo nivel Otros')
            ticket.set_wait_time('Level_Others', env.now - ticket.sum_waiting_times())

    elif siguiente == "productOwner":
        if env.now < 28800: # antes de las 8 hs no lo atienden
            yield env.timeout(28800 - env.now)
        if env.now > 61200: # despues de las 17 hs no lo atienden
            yield env.timeout(86400 - env.now) # termina el dia y no lo atienden
        with emp_prodOwn.request() as req: 
            yield req
            yield env.timeout(max(60, np.random.uniform(MEDIA_NIVEL_PRODUCT_OWNER, DESVIO_NIVEL_PRODUCT_OWNER)))
            print(f'{time.strftime("%H:%M:%S", time.gmtime(env.now))}{ticket.descripcion}: finalizo nivel Product Owner')
            ticket.set_wait_time('Level_ProductOwner', env.now - ticket.sum_waiting_times())


    print(f'***************{time.strftime("%H:%M:%S", time.gmtime(env.now))} {ticket.descripcion} : RESUELTO *****************************')

    ticketsResueltos.append(ticket)
    wait_times.append(sum(ticket.wait_time.values()))


def calculate_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

def main():
    # Setup
    random.seed(42) # fijo la semilla para que me de los mismos valores
    
    # Corremos la simulacion
    env = simpy.Environment()
    env.process(Arrivals(env))
    env.run(until=TIEMPO_SIMULACION)

    # resultados
    waiting_times_level_one = sum(i.wait_time["Level_One"] for i in ticketsArribados )
    waiting_times_level_apps = sum(i.wait_time["Level_Apps"] for i in ticketsArribados )
    waiting_times_level_hardw = sum(i.wait_time["Level_Hardware"] for i in ticketsArribados )
    waiting_times_level_other = sum(i.wait_time["Level_Others"] for i in ticketsArribados )
    waiting_times_level_productOwner = sum(i.wait_time["Level_ProductOwner"] for i in ticketsArribados )
    tot = waiting_times_level_one+waiting_times_level_apps+waiting_times_level_hardw+waiting_times_level_other+waiting_times_level_productOwner
    print("-----------------------------------------------------------------------------------------------")
    print(f"Tickets resueltos: {len(ticketsResueltos)} ")
    print(f"Tickets empezados pero sin resolver: {len(ticketsArribados)-len(ticketsResueltos)} ")
    print(f"\nTIEMPOS DE ESPERA TOTALES:{tot}" )
    mins, secs = calculate_wait_time(wait_times)
    print(

            f"\nEl tiempo promedio es {mins} minutos y {secs} segundos.",
        )
        
    print("\nTIEMPOS DE ESPERA POR NIVEL:")
    print(f"Nivel 1: {waiting_times_level_one}s --> {(waiting_times_level_one/tot):.2%}")
    print(f"Nivel Apps: {waiting_times_level_apps}s --> {(waiting_times_level_apps/tot):.2%}")
    print(f"Nivel Hardware: {waiting_times_level_hardw}s --> {(waiting_times_level_hardw/tot):.2%}")
    print(f"Nivel Otros: {waiting_times_level_other}s --> {(waiting_times_level_other/tot):.2%}")
    print(f"Nivel Product owner: {waiting_times_level_productOwner}s --> {(waiting_times_level_productOwner/tot):.2%}")

    
    ##Plotting results
    y = np.array([waiting_times_level_one, waiting_times_level_apps, waiting_times_level_hardw, waiting_times_level_other,waiting_times_level_productOwner])
    labels = ["Level 1", "Level Apps", "Level Hardware", "Level Otros","Level Product Owner"]
    fig, ax = plt.subplots()
    ax.pie(y, labels = labels, autopct='%1.1f%%')
    plt.title("Porcentajes de los tiempos de espera por cola", bbox={'facecolor':'0.8', 'pad':5})
    plt.show() 

    y = np.array([ len(ticketsResueltos), len(ticketsArribados) - len(ticketsResueltos)])
    labels = ["Tickets Resueltos", "Tickets Arribados sin resolver"]
    fig, ax = plt.subplots()
    ax.pie(y, labels = labels, autopct='%1.1f%%')
    plt.title("Proporción de tickets resueltos y los qye no pudieron ser finalizados en 24hs", bbox={'facecolor':'0.8', 'pad':5})
    plt.show() 

if __name__ == '__main__':
    main()