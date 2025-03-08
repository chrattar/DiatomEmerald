import pygame
import random
import numpy as np
import sys
import config as cfg
import matplotlib.pyplot as plt
import time
from collections import defaultdict
from assets_loader import AssetManager
from entities import Cell, Predator, Plant, Omnivore

# Init Pygame
pygame.init()
pygame.font.init()

# Global variables
width, height = cfg.WIDTH, cfg.HEIGHT
regeneration_delay = cfg.REGENERATION_DELAY
population_history = defaultdict(list)
time_points = []
RECORD_INTERVAL = 5000  # Millisecs
last_record_time = pygame.time.get_ticks()
#DISPLAY
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Particle Simulation")
font_size = 20
font = pygame.font.SysFont("Helvetica", font_size)

def draw_text(screen, text, position, font, color=(255,255,255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def plot_population_history():
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, population_history['cells'], label='Cells', color='cyan')
    plt.plot(time_points, population_history['plants'], label='Plants', color='green')
    plt.plot(time_points, population_history['predators'], label='Predators', color='red')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Population')
    plt.title('Population Changes Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('population_history.png')
    plt.close()

def main():
    clock = pygame.time.Clock()
    cells = [Cell() for _ in range(cfg.CELLS_NUM)]
    plants = [Plant() for _ in range(cfg.PLANTS_NUM)]
    preds = [Predator() for _ in range(cfg.PREDATORS_NUM)]
    omnivores = [Omnivore() for _ in range(cfg.OMNIVORE_NUM)]  
    is_paused = False
    last_record_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                plot_population_history()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_paused = not is_paused

        if not is_paused:
            screen.fill((0, 90, 90))

            # PRED UPDATE DRAW
            for pred in preds[:]:
                mutation = pred.update(cells, current_time, preds)
                if mutation:
                    preds.remove(pred)
                    omnivores.append(mutation)
                pred.draw()

            #CELL UPDATE DRAW
            for cell in cells[:]:
                mutation = cell.update(cells)
                if mutation:
                    cells.remove(cell)
                    omnivores.append(mutation)
                cell.draw()
                for plant in plants:
                    if cell.consume_plant(plant, current_time):
                        plant.active = False
                        plant.regeneration_time = current_time + regeneration_delay

            # PLAT - UPDATE DRAWR
            for plant in plants:
                plant.update(plants)
                plant.draw()
            
           #OMNIVORE UPDATE DRAW
            for omnivore in omnivores[:]:
                omnivore.update(cells, plants, omnivores, current_time)
                omnivore.draw()

            # REMOVE DEAD
            cells = [cell for cell in cells if cell.active and cell.energy > 0]
            plants = [plant for plant in plants if plant.active]
            preds = [pred for pred in preds if pred.energy > 0]
            omnivores = [omni for omni in omnivores if omni.energy > 0]

            # IS ERVYTHING DEAD
            if len(cells) == 0 and len(preds) == 0 and len(plants) == 0 and len(omnivores) == 0:
                plot_population_history()
                print("Simulation ended: No more cells, predators, or omnivores.")
                pygame.quit()   
                sys.exit()

            # WHATS ALIVE
            active_cells_count = len(cells)
            active_plants_count = len(plants)
            active_preds_count = len(preds)
            active_omnivores_count = len(omnivores)

            # SCREEN COUNTER
            draw_text(screen, f"Cells: {active_cells_count}", (10, 10), font, color=(0, 255, 255))
            draw_text(screen, f"Plants: {active_plants_count}", (10, 40), font, color=(0, 255, 0))
            draw_text(screen, f"Preds: {active_preds_count}", (10, 70), font, color=(255, 0, 0))
            draw_text(screen, f"Omnis: {active_omnivores_count}", (10, 100), font, color=(255, 0, 145))  # Fixed y position

            # LOG POP HIST
            if current_time - last_record_time >= RECORD_INTERVAL:
                time_seconds = current_time / 1000
                time_points.append(time_seconds)
                population_history['cells'].append(active_cells_count)
                population_history['plants'].append(active_plants_count)
                population_history['predators'].append(active_preds_count)
                population_history['omnivores'].append(active_omnivores_count)
                last_record_time = current_time

        else:
            pause_text = font.render("Paused", True, (255, 0, 0))
            screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, 
                                    height // 2 - pause_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    main()