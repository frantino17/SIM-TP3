from flask import Flask, render_template, request 
import random
import os
import json
app = Flask(__name__)

# Definir las probabilidades en función de la estrategia
def define_probabilities(n):
    if n == 42:
        probabilities = {
            38: 0.10,
            39: 0.25,
            40: 0.40,
            41: 0.15,
            42: 0.10,
        }
        return probabilities
    if n == 43:
        probabilities = {
            38: 0.05,
            39: 0.25,
            40: 0.45,
            41: 0.15,
            42: 0.05,
            43: 0.05
        }
        return probabilities
    if n == 44:
        probabilities = {
            38: 0,
            39: 0.05,
            40: 0.20,
            41: 0.45,
            42: 0.15,
            43: 0.05,
            44: 0.1
        }
        return probabilities
    return ValueError("La estrategia elegida debe estar entre los valores")

def get_strategy(random_value, probabilities):
    cumulative_probability = 0.0
    for strategy, probability in probabilities.items():
        cumulative_probability += probability
        if random_value <= cumulative_probability:
            return strategy
    # Si por algún motivo no se devuelve ninguna estrategia, podrías lanzar un error.
    raise ValueError("La probabilidad proporcionada no es válida o no suma correctamente a 1.")


# Función que realiza la simulación de Monte Carlo
def montecarlo_simulation(simulation_size, probabilities_strategy, utility_per_passenger):
    # Definir probabilidades basadas en el problema
    probabilities = define_probabilities(probabilities_strategy)
    
    # Parámetros de utilidad
    overbooking_cost = 150
    # Acumuladores
    total_utility = 0
    denied_passengers_total = 0
    vector = []  # Vector para almacenar los resultados de cada simulación
    
    # Realizar las simulaciones
    for i in range(1, simulation_size + 1):
        # Obtenes random y lo redondeas a 4 decimales
        rnd = round(random.random(),4)
        #Para evitar errores de coma flotante
        rnd = rnd - 1e-15 if rnd == 1 else rnd
        passengers_show_up = get_strategy(rnd,probabilities)

        capacity = 40  # Siempre es la misma capacidad
        # Calcular la utilidad del vuelo
        admitted_passengers = min(passengers_show_up, capacity)
        denied_passengers = max(passengers_show_up - capacity, 0)
        denied_passengers_total += denied_passengers
        
        # Utilidad es la suma de los ingresos menos el costo de los pasajeros no admitidos
        utility = (admitted_passengers * utility_per_passenger) - (denied_passengers * overbooking_cost)
        total_utility += utility

        # Crear un diccionario con los datos
        flight_data = {
            "numero_vuelo": i,  # Número de vuelo
            "random": rnd,  # Número Random
            "estrategia_random": passengers_show_up,  # Probabilidad correspondiente al numero Random
            "admitted_passengers": admitted_passengers,  # Pasajeros admitidos
            "denied_passengers": denied_passengers,  # Pasajeros que no pudieron abordar
            "utility": utility,  # Utilidad del vuelo
            "denied_passengers_total": denied_passengers_total,  # Acumulador de pasajeros denegados
            "total_utility": total_utility
        }
        
        # Agregar el objeto (diccionario) al vector
        vector.append(flight_data)
    
    # Devolver el vector con todas las simulaciones
    return vector


def save_utility_simulation(size, strategy, utility, total_utility):
    avg_utility = total_utility / size
    simulation_data = {
        "size": size,
        "strategy": strategy,
        "utility_per_passenger": utility,
        "average_utility": avg_utility
    }    
    file_path = os.path.join(os.getcwd(), 'resultados.json')
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            try:
                existing_data = json.load(json_file) 
            except json.JSONDecodeError:
                existing_data = []  
    else:
        existing_data = []  

    existing_data.append(simulation_data)
  
    with open(file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para realizar la simulación
@app.route('/simulate', methods=['POST'])
def simulate():
    # Obtener los parámetros de la forma
    N = int(request.form['N'])
    from_ = int(request.form['A'])
    to = int(request.form['B'])
    strategy = int(request.form['strategy'])
    utility_per_passenger = int(request.form['utility_per_passanger'])

    # Realizar la simulación
    vector = montecarlo_simulation(N, strategy, utility_per_passenger)
    # Filtras el array para mostrar solo las filas que se piden en el form
    sliced_vector = vector[from_:to:1]

    save_utility_simulation(N,strategy,utility_per_passenger, vector[-1]["total_utility"])
    # Mostrar la última fila de la simulación
    return render_template('result.html', last_row=vector[-1], full_vector=sliced_vector,strategy = strategy, size= N)

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
