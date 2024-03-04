import simpy
import random
import statistics
import matplotlib.pyplot as plt
from Tarea_C_Hoja5 import TIEMPOS_PROMEDIO

# Parámetros de la simulación
RANDOM_SEED = 42
MEMORIA_RAM = 100
VELOCIDAD_CPU = 3  # Número de instrucciones por unidad de tiempo
NUM_PROCESOS = [25, 50, 100, 150, 200]
INTERVALOS_LLEGADA = [10, 5, 1]
TIEMPO_MAXIMO = 100

def proceso(env, nombre, memoria, cpu, tiempo_total, io_list):
    llegada = env.now
    print(f'{nombre} llega al sistema en el tiempo {llegada}')

    # Generar un número aleatorio para la memoria necesaria
    memoria_necesaria = random.randint(1, 10)

    # Solicitar memoria
    with memoria.get(memoria_necesaria) as req:
        yield req

        # Listo para ejecutar
        ready_time = env.now
        print(f'{nombre} está listo para ejecutar en el tiempo {ready_time}')

        instrucciones_restantes = random.randint(1, 10)

        while instrucciones_restantes > 0:
            # Usar CPU
            with cpu.request() as req:
                yield req
                # Ejecutar instrucciones
                instrucciones_ejecutadas = min(instrucciones_restantes, VELOCIDAD_CPU)
                instrucciones_restantes -= instrucciones_ejecutadas
                yield env.timeout(1)  # El tiempo que toma ejecutar instrucciones
                print(f'{nombre} ejecuta {instrucciones_ejecutadas} instrucciones en el tiempo {env.now}')

                # Verificar si el proceso terminó
                if instrucciones_restantes <= 0:
                    break

                # Decidir si va a I/O, a ready o continúa corriendo
                if random.random() < 0.1:  # Probabilidad de 10% de ir a I/O
                    # Va a I/O
                    io_list.append(env.process(io_proceso(env, nombre)))
                    break
                elif random.random() < 0.2:  # Probabilidad de 20% de ir a ready
                    # Va a ready
                    break

        # Proceso terminado
        terminado_time = env.now
        tiempo_total.append(terminado_time - llegada)
        memoria.put(memoria_necesaria)  # Devolver memoria
        print(f'{nombre} termina en el tiempo {terminado_time}')

def io_proceso(env, nombre):
    # Simulación de operación de I/O
    yield env.timeout(1)
    print(f'{nombre} realiza operaciones de I/O en el tiempo {env.now}')

def ejecutar_simulacion(env, num_procesos, tiempo_simulacion, intervalo_llegada):
    memoria = simpy.Container(env, init=MEMORIA_RAM, capacity=MEMORIA_RAM)
    cpu = simpy.Resource(env, capacity=1)

    tiempo_total = []  # Reiniciar la lista tiempo_total para cada ejecución
    io_list = []  # Lista para almacenar los procesos de I/O

    # Generar procesos
    for i in range(num_procesos):
        env.process(proceso(env, f'Proceso {i}', memoria, cpu, tiempo_total, io_list))

    # Ejecutar simulación hasta que se alcance el tiempo máximo
    yield env.timeout(tiempo_simulacion)

    # Calcular el tiempo promedio y devolverlo como resultado
    tiempo_promedio = statistics.mean(tiempo_total)
    return tiempo_promedio

def ejecutar_tarea_a():
    tiempos_promedio = []
    desviaciones_estandar = []

    for num_procesos in NUM_PROCESOS:
        env = simpy.Environment()
        tiempo_promedio_iteracion = []
        for _ in range(5):
            env.process(ejecutar_simulacion(env, num_procesos, TIEMPO_MAXIMO, INTERVALOS_LLEGADA[0]))  # Intervalo de llegada de 10
            env.run()  # Ejecutar la simulación
            tiempo_promedio_iteracion.append(statistics.mean(TIEMPOS_PROMEDIO))
        tiempos_promedio.append(statistics.mean(tiempo_promedio_iteracion))
        desviaciones_estandar.append(statistics.stdev(tiempo_promedio_iteracion))

    # Graficar resultados para la tarea a
    plt.errorbar(NUM_PROCESOS, tiempos_promedio, yerr=desviaciones_estandar, fmt='o')
    plt.xlabel('Número de Procesos')
    plt.ylabel('Tiempo Promedio')
    plt.title('Número de Procesos vs Tiempo Promedio (Intervalo de llegada = 10)')
    plt.show()

def ejecutar_tarea_b():
    for intervalo in INTERVALOS_LLEGADA:
        tiempos_promedio = []

        for num_procesos in NUM_PROCESOS:
            env = simpy.Environment()
            tiempo_promedio_iteracion = []
            for _ in range(5):
                env.process(ejecutar_simulacion(env, num_procesos, TIEMPO_MAXIMO, intervalo))
                env.run()  # Ejecutar la simulación
                tiempo_promedio_iteracion.append(statistics.mean(TIEMPOS_PROMEDIO))
            tiempos_promedio.append(statistics.mean(tiempo_promedio_iteracion))

        # Graficar resultados para la tarea b
        plt.plot(NUM_PROCESOS, tiempos_promedio, label=f'Intervalo = {intervalo}')

    plt.xlabel('Número de Procesos')
    plt.ylabel('Tiempo Promedio')
    plt.title('Número de Procesos vs Tiempo Promedio (Diferentes Intervalos de Llegada)')
    plt.legend()
    plt.show()

def ejecutar_tarea_c():
    ESTRATEGIAS = [
        ("Incrementar memoria a 200", 200, MEMORIA_RAM, VELOCIDAD_CPU),
        ("Restaurar memoria a 100 y aumentar velocidad de CPU a 6", MEMORIA_RAM, 6, 1),
        ("Restaurar velocidad de CPU a 3 y emplear 2 procesadores", MEMORIA_RAM, VELOCIDAD_CPU, 2)
    ]

    for nombre_estrategia, memoria_estrategia, velocidad_estrategia, num_cpus_estrategia in ESTRATEGIAS:
        print(f"Estrategia: {nombre_estrategia}")
        tiempos_promedio = []

        for num_procesos in NUM_PROCESOS:
            env = simpy.Environment()
            memoria = simpy.Container(env, init=memoria_estrategia, capacity=memoria_estrategia)
            cpu = simpy.Resource(env, capacity=num_cpus_estrategia)
            tiempo_promedio_iteracion = []
            for _ in range(5):
                env.process(ejecutar_simulacion(env, num_procesos, TIEMPO_MAXIMO, INTERVALOS_LLEGADA[0]))  # Intervalo de llegada de 10
                env.run()  # Ejecutar la simulación
                tiempo_promedio_iteracion.append(statistics.mean(TIEMPOS_PROMEDIO))
            tiempos_promedio.append(statistics.mean(tiempo_promedio_iteracion))

        # Graficar resultados para la estrategia actual
        plt.plot(NUM_PROCESOS, tiempos_promedio, label=nombre_estrategia)
        plt.xlabel('Número de Procesos')
        plt.ylabel('Tiempo Promedio')
        plt.title('Número de Procesos vs Tiempo Promedio (Intervalo de llegada = 10)')
        plt.legend()
        plt.show()

# Ejecutar las tareas
ejecutar_tarea_a()
ejecutar_tarea_b()
ejecutar_tarea_c()
