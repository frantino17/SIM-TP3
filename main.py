from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import random

app = Flask(__name__)

# Variable global para almacenar las simulaciones
simulaciones = []

def montecarlo(n, revenue_per_passenger, overbooking_cost, prob_distribution):
    utilidades = []
    filas = []
    
    for i in range(n):
        # Generar el número de pasajeros que se presentan basado en la distribución de probabilidad
        pasajeros_presentes = np.random.choice(list(prob_distribution.keys()), p=list(prob_distribution.values()))
        
        # Calcular la utilidad basada en la cantidad de pasajeros presentes
        if pasajeros_presentes <= 40:
            utilidad = pasajeros_presentes * revenue_per_passenger
            overbooking_cost_final = 0
        else:
            utilidad = 40 * revenue_per_passenger
            overbooking_cost_final = (pasajeros_presentes - 40) * overbooking_cost
            utilidad -= overbooking_cost_final

        utilidades.append(utilidad)
        
        # Guardar los datos de cada fila
        filas.append({
            'index': i + 1,  # Para que empiece en 1
            'accepted_reservations': 40,
            'passengers_presented': pasajeros_presentes,
            'utility': utilidad,
            'overbooking_cost': overbooking_cost_final
        })

    # Calcular la utilidad promedio por vuelo
    utilidad_promedio = np.mean(utilidades)
    
    return utilidad_promedio, filas

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener los parámetros del formulario
        simulation_time = int(request.form['simulation_time'])
        num_rows = int(request.form['num_rows'])
        iterations = int(request.form['iterations'])
        start_hour = int(request.form['start_hour'])
        revenue_per_passenger = int(request.form['revenue_per_passenger'])
        overbooking_cost = int(request.form['overbooking_cost'])

        # Distribuciones de probabilidad ingresadas por el usuario
        prob_42 = {
            38: float(request.form['prob_42_38']),
            39: float(request.form['prob_42_39']),
            40: float(request.form['prob_42_40']),
            41: float(request.form['prob_42_41']),
            42: float(request.form['prob_42_42']),
            43: float(request.form['prob_42_43']),
            44: float(request.form['prob_42_44']),
        }

        # Simulación para 42 reservaciones
        utilidad_promedio_42, filas_42 = montecarlo(num_rows, revenue_per_passenger, overbooking_cost, prob_42)

        # Calcular los valores totales para mostrar en el resumen
        total_utility = sum(fila['utility'] for fila in filas_42)
        total_overbooking_cost = sum(fila['overbooking_cost'] for fila in filas_42)
        last_row = filas_42[-1]  # Última fila simulada

        # Obtener las iteraciones a partir de la hora j
        displayed_rows = filas_42[start_hour - 1:start_hour - 1 + iterations]

        # Almacenar la simulación actual
        simulaciones.append({
            'num_rows': num_rows,
            'iterations': iterations,
            'start_hour': start_hour,
            'revenue_per_passenger': revenue_per_passenger,
            'overbooking_cost': overbooking_cost,
            'utilidad_promedio_42': utilidad_promedio_42,
            'filas': filas_42,
            'total_utility': total_utility,
            'total_overbooking_cost': total_overbooking_cost
        })

        return render_template(
            'result.html',
            average_utility=utilidad_promedio_42,
            average_overbooking_cost=total_overbooking_cost / num_rows,
            start_hour=start_hour,
            iterations=iterations,
            displayed_rows=displayed_rows,
            last_row=last_row,
            total_rows=num_rows,
            total_utility=total_utility,
            total_overbooking_cost=total_overbooking_cost
        )

    return render_template('index.html')

@app.route('/eliminar', methods=['POST'])
def eliminar():
    global simulaciones
    simulaciones = []
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
