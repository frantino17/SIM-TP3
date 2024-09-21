from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Función que realiza la simulación de Monte Carlo
def montecarlo_simulation(reservations, capacity, num_simulations=10000):
    # Definir probabilidades basadas en el problema
    probabilities = {
        38: 0.05,
        39: 0.25,
        40: 0.45,
        41: 0.15,
        42: 0.05,
        43: 0.05
    }
    
    # Parámetros de utilidad
    revenue_per_passenger = 100
    overbooking_cost = 150
    
    total_utility = 0
    
    for _ in range(num_simulations):
        # Simular cuántos pasajeros se presentan según las probabilidades
        passengers_show_up = random.choices(list(probabilities.keys()), weights=probabilities.values())[0]
        
        # Calcular la utilidad del vuelo
        admitted_passengers = min(passengers_show_up, capacity)
        denied_passengers = max(passengers_show_up - capacity, 0)
        
        # Utilidad es la suma de los ingresos menos el costo de los pasajeros no admitidos
        utility = (admitted_passengers * revenue_per_passenger) - (denied_passengers * overbooking_cost)
        total_utility += utility
    
    # Devolver la utilidad promedio
    return total_utility / num_simulations

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para realizar la simulación
@app.route('/simulate', methods=['POST'])
def simulate():
    # Obtener los parámetros de la forma
    reservations = int(request.form['reservations'])
    capacity = int(request.form['capacity'])
    
    # Realizar la simulación
    average_utility = montecarlo_simulation(reservations, capacity)
    
    return render_template('result.html', average_utility=average_utility)

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
