import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Parámetros de la simulación
RANDOM_SEED = 42
MEMORIA_RAM = 100
VELOCIDAD_CPU = 3  # Número de instrucciones por unidad de tiempo
NUM_PROCESOS = [25, 50, 100, 150, 200]
INTERVALOS_LLEGADA = [10, 5, 1]
TIEMPOS_PROMEDIO = []

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

    # Generar procesos con el intervalo de llegada dado
    for i in range(num_procesos):
        env.process(proceso(env, f'Proceso {i}', memoria, cpu, tiempo_total, io_list))
        yield env.timeout(intervalo_llegada)

    # Ejecutar simulación hasta que se alcance el tiempo máximo
    yield env.timeout(tiempo_simulacion)

    # Calcular el tiempo promedio y devolverlo como resultado
    tiempo_promedio = statistics.mean(tiempo_total)
    TIEMPOS_PROMEDIO.append(tiempo_promedio)

# Configurar la simulación
random.seed(RANDOM_SEED)

# Definir el tiempo máximo de simulación
tiempo_maximo = 100  # Por ejemplo, establece un tiempo máximo de 100 unidades de tiempo

# Ejecutar la simulación para diferentes cantidades de procesos y intervalos de llegada
for intervalo_llegada in INTERVALOS_LLEGADA:
    TIEMPOS_PROMEDIO = []  # Reiniciar la lista de tiempos promedio para cada intervalo de llegada
    for num_procesos in NUM_PROCESOS:
        env = simpy.Environment()
        env.process(ejecutar_simulacion(env, num_procesos, tiempo_maximo, intervalo_llegada))  # Ejecutar la simulación
        env.run()  # Ejecutar la simulación hasta que se alcance el tiempo máximo

    # Graficar resultados para el intervalo de llegada actual
    plt.plot(NUM_PROCESOS, TIEMPOS_PROMEDIO, label=f'Intervalo de llegada: {intervalo_llegada}')
    plt.xlabel('Número de Procesos')
    plt.ylabel('Tiempo Promedio')
    plt.title('Número de Procesos vs Tiempo Promedio')
    plt.legend()
    plt.show()
