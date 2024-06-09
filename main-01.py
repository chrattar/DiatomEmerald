import pygame
import random
import numpy as np
import sys
import config as cfg
import pandas as pandas
import matplotlib.pyplot as plt
import threading
from assets_loader import AssetManager
import time
from entities import Cell, Predator, Plant
#Init Pygame
pygame.init()
pygame.font.init()

counts_log = []  # Stores the count logs
last_log_time = pygame.time.get_ticks()
log_interval = 1000  # Do the same for any other global variables you're using
last_log_time =  pygame.time.get_ticks()

#Font
font_size = 20
font = pygame.font.SysFont("Verdana", font_size)

width, height = cfg.WIDTH, cfg.HEIGHT
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Particle Simulation")
regeneration_delay = cfg.REGENERATION_DELAY

def draw_text(screen, text, position, font, color=(255,255,255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def main():
    clock = pygame.time.Clock()
    cells = [Cell() for _ in range(cfg.CELLS_NUM)]  # Create NUM_PARTICLES particles count
    plants = [Plant() for _ in range(cfg.PLANTS_NUM)] # Create NUM_PLANTS
    preds = [Predator() for _ in range(cfg.PREDATORS_NUM)]
    last_update = pygame.time.get_ticks()
    is_paused = False  # Initialize is_paused outside the loop


    while True:
        #current_time = pygame.time.get_ticks()
        current_time = time.time()#pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # 'p' key to pause the game
                    is_paused = not is_paused

        if not is_paused:
            screen.fill((0, 90, 90))  # Clear the screen only if not paused

            # Game logic here...
            for pred in preds[:]:
                pred.update(cells, current_time)
                pred.draw()

            #for cell in cells[:]:  #   cell.update(cells)  #  cell.draw() # if pred.consume_cell(cell, current_time): #    cell.active = False

            for cell in cells:
                cell.update(cells)  # Update cell position, energy, etc.
                cell.draw()
                for plant in plants:
                    if cell.consume_plant(plant, current_time):
                        plant.active = False
                        plant.regeneration_time = current_time + regeneration_delay   # Ensure this method checks plant's active status
                        # Handle plant consumption logic here (e.g., deactivate plant, increase cell energy)
                        #cell.draw()
                        
               # for plant in plants:  #    plant.draw()#   if not plant.active and current_time - plant.regeneration_time >= 0:#      plant.reset_position()#     plant.active = True
            for plant in plants[:]:
                plant.update(plants)
                plant.draw()
            plants = [plant for plant in plants if plant.active]
               # if not plant.active and current_time >= plant.regeneration_time:
                #    plant.reset_position()
                 #   plant.active = True
           
    # Remove inactive cells
            cells = [cell for cell in cells if cell.active]

                # Display active counts
            active_cells_count = sum(1 for cell in cells if cell.energy > 0)
            active_plants_count = sum(1 for plant in plants if plant.active)
            active_preds_count = sum(1 for pred in preds if pred.energy > 0)
            draw_text(screen, f"Cells: {active_cells_count}", (10, 10), font, color=(0, 255, 255))
            draw_text(screen, f"Plants: {active_plants_count}", (10, 40), font, color=(0, 255, 0))
            draw_text(screen, f"Preds: {active_preds_count}", (10,70), font, color=(255, 0, 0))
        else:
            # Display a pause message
            pause_text = font.render("Paused", True, (255, 0, 0))
            screen.blit(pause_text, (width // 2 - pause_text.get_width() // 2, height // 2 - pause_text.get_height() // 2))

        pygame.display.flip()  # Update the display once per loop iteration
        clock.tick(30)  # Control the frame rate

        if not is_paused:
            cells = [p for p in cells if p.energy > 0]  # Remove cells with no energy outside of pause
            plants = [plant for plant in plants if plant.active]  # Optionally clean up inactive plants
if __name__ == "__main__":
    main()