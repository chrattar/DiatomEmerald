import random
import config as cfg
import time
import json
import uuid
from collections import defaultdict
from entities import Cell, Predator, Plant, Omnivore
from spatialgrid import SpatialGrid

def run_headless_simulation(params, max_runtime=1000):
    #INIT CONFIG
    cells = [Cell() for _ in range(params['CELLS_NUM'])]
    plants = [Plant() for _ in range(params['PLANTS_NUM'])]
    preds = [Predator() for _ in range(params['PREDATORS_NUM'])]
    omnivores = [Omnivore() for _ in range(params['OMNIVORE_NUM'])]
    start_time = time.time()
    current_time = 0
    population_history = defaultdict(list)
    time_points = []
    
    #MAIN WITH NO PYGAME
    while time.time() - start_time < max_runtime:
        current_time = int((time.time() - start_time) * 1000)  # Convert to ms
        
        #PRED UPDATE
        for pred in preds[:]:
            mutation = pred.update(cells, current_time, preds)
            if mutation:
                preds.remove(pred)
                omnivores.append(mutation)
        
        # CELL UPDATE
        for cell in cells[:]:
            mutation = cell.update(cells)
            if mutation:
                cells.remove(cell)
                omnivores.append(mutation)
            for plant in plants:
                if cell.consume_plant(plant, current_time):
                    plant.active = False
                    plant.regeneration_time = current_time + cfg.REGENERATION_DELAY
        
        # PLANTS AND OMINVORES
        for plant in plants:
            plant.update(plants)
        
        for omnivore in omnivores[:]:
            omnivore.update(cells, plants, omnivores, current_time)
        
        # REMOVE DEAD
        cells = [cell for cell in cells if cell.active and cell.energy > 0]
        plants = [plant for plant in plants if plant.active]
        preds = [pred for pred in preds if pred.energy > 0]
        omnivores = [omni for omni in omnivores if omni.energy > 0]
        if len(cells) == 0 and len(preds) == 0 and len(plants) == 0 and len(omnivores) == 0: #<--- Extinction clean
            break
        
        #RECORD COUNT
        if current_time % 1000 < 10:  # Record approximately every second
            time_seconds = current_time / 1000
            time_points.append(time_seconds)
            population_history['cells'].append(len(cells))
            population_history['plants'].append(len(plants))
            population_history['predators'].append(len(preds))
            population_history['omnivores'].append(len(omnivores))
    
    elapsed_time = time.time() - start_time
    return {
            'runtime': elapsed_time,
            'start_populations': {
                'cells': params['CELLS_NUM'],
                'plants': params['PLANTS_NUM'],
                'predators': params['PREDATORS_NUM'],
                'omnivores': params['OMNIVORE_NUM']
            },
            #'final_populations': {
             #   'cells': len(cells),
              #  'plants': len(plants),
               # 'predators': len(preds),
                #'omnivores': len(omnivores)
            #},
            'population_history': dict(population_history),
            'time_points': time_points
        }

def monte_carlo(num_iterations=100):
    results = []
    
    for i in range(num_iterations):
        run_id = str(uuid.uuid4())[:8]
        print(f"Running simulation {i+1}/{num_iterations} (ID: {run_id})")
        
        # Generate random parameters
        params = {
            'CELLS_NUM': random.randint(10, 100),
            'PLANTS_NUM': random.randint(10, 100),
            'PREDATORS_NUM': random.randint(5, 50),
            'OMNIVORE_NUM': random.randint(5, 50)
        }
        
        sim_result = run_headless_simulation(params)
        
        results.append({
            'run_id': run_id,
            'params': params,
            'runtime': sim_result['runtime'],
            'start': sim_result['start_populations']
        })
    
    # Save results to file
    with open('monte_carlo_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Completed {num_iterations} simulations, results saved to monte_carlo_results.json")
    return results

if __name__ == "__main__":
    monte_carlo(10)  # Start with 10 iterations
