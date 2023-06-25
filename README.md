# HelpDeskSimulation
This is a work done for the systems simulation course. We simulate the model of a Help Desk in GPSS, ProModel and Python languages (using simpy).

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

Horario de atención del Product Owner: 8 a 17 hs

#SUPUESTOS : Este codigo sirve para simular la jornada laboral de un solo dia, hay que modificar los valores si deseamos simular mas
