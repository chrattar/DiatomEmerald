import pygame
import random
import numpy as np
import sys
import config as cfg
import matplotlib.pyplot as plt
import threading
from assets_loader import AssetManager
import time

width, height = cfg.WIDTH, cfg.HEIGHT
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Particle Simulation")
regeneration_delay = cfg.REGENERATION_DELAY

#Assets - pulled from assets_loader.py
assets = AssetManager()
energy_start = cfg.ENERGY_INITIAL
energy_cell_max = cfg.CELL_ENERGY_MAX
energy_plant = cfg.PLANTS_ENERGY
energy_plant_max = cfg.PLANTS_ENERGY_MAX
energy_pred = cfg. PREDATOR_ENERGY_INITAL
#sprite_image = pygame.image.load('sprite.png').convert_alpha() For local load
img_cell = assets.get_image('sprite1')
#cell_new = assets.get_image('sprite4')
img_plant = assets.get_image('sprite2')
img_pred = assets.get_image('sprite3')

# Particle class definitions
class Cell:
    def __init__(self, 
                 energy=energy_start,
                 energy_efficiency=1.0):
        self.image = img_cell
        self.max_energy = energy_cell_max
        self.energy = energy
        self.active = True
        self.rect = self.image.get_rect()
        # Initialize the particle at a random position
            #Width - self.rect.width - Select a random int between 0 and the screen width-self width
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)
        self.mutation_rate_cell = cfg.MUTATION_RATE
   
    def divide(self, cells_list):
        if self.energy < cfg.DIVISION_THRESHOLD:
            self.divide(cells_list)
        self.energy = cfg.ENERGY_INITIAL  # Parent keeps half its energy
        new_cell = Cell(self.energy)  # Create a new cell with the same energy level

        # Slightly offset the new cell from the parent
        offset = random.randint(-2, 2)  # Adjust the offset value as needed
        new_cell.rect.x = max(0, min(self.rect.x + offset, width - new_cell.rect.width))
        new_cell.rect.y = max(0, min(self.rect.y + offset, height - new_cell.rect.height))
        cells_list.append(new_cell)                                      
    
    def draw_energy_bar(self):
        bar_length = 20
        bar_height = 5
        energy_ratio = self.energy / self.max_energy
        energy_length = bar_length * bar_height
        #filled_length = int(self.energy /self.max_energy * bar_length)
        filled_length = int(energy_ratio * bar_length)
        bar_x = self.rect.centerx - bar_length // 2
        bar_y = self.rect.top - bar_height -5
        # Draw background of energy bar
        background_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_length, bar_height)
        pygame.draw.rect(screen, (0,0,0), background_rect)
        #Draw Current Energy Level
        filled_rect = pygame.Rect(self.rect.x, self.rect.y-10, filled_length, bar_height)
        pygame.draw.rect(screen, (140,0,0),filled_rect)                 

    def consume_plant(self, plant, current_time):
        if self.rect.colliderect(plant.rect) and plant.active:
            print(f"Plant consumed by cell at {self.rect.topleft}")
            self.energy += plant.energy
            plant.active = False
            plant.regeneration_time = current_time + regeneration_delay
            return True
        return False
   
    def add_energy(self, amount):
        #Increase but dont exceed max energy
        self.energy += amount
        if self.energy > self.max_energy:
            self.energy = self.max_energy
    def draw(self):
        if self.energy >0:
            screen.blit(self.image, self.rect)
            self.draw_energy_bar()
    
    def update(self, cells_list):
        if self.energy <= 0:
            return 
        self.move()
        self.energy -= cfg.CELL_ENERGY_DECAY  # Energy decay over time

        while self.energy >= cfg.DIVISION_THRESHOLD:
            self.divide(cells_list)
        
    def move(self):  # Ensure this method is correctly indented to be part of the Particle class
        # Simple movement logic: move the particle randomly
        self.rect.x += random.randint(-10, 10)
        self.rect.y += random.randint(-10, 10)
        # Keep the particle within the screen bounds
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))
        pass

class Plant:
    def __init__(self,
                 energy = energy_plant,
                 energy_efficiency=1.0):
        self.image = img_plant
        self.rect = self.image.get_rect()
        self.active = True
        #self.reset_position()
        #below would manually set position. ResetPosition is doing this for me right now
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)
        self.energy = energy_plant 
        self.max_energy = energy_plant_max
         # Fixed amount of energy the plant provides
        self.regeneration_time = 0 #pygame.time.get_ticks() +f 15000
        self.last_division_time = time.time()
        self.decay = cfg.PLANT_DECAY

    def draw_energy_bar(self):
        bar_length = 20
        bar_height = 5
        energy_ratio = self.energy / self.max_energy
        energy_length = bar_length * bar_height
        #filled_length = int(self.energy /self.max_energy * bar_length)
        filled_length = int(energy_ratio * bar_length)
        bar_x = self.rect.centerx - bar_length // 2
        bar_y = self.rect.top - bar_height -5
        # Draw background of energy bar
        background_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_length, bar_height)
        pygame.draw.rect(screen, (0,0,0), background_rect)
        #Draw Current Energy Level
        filled_rect = pygame.Rect(self.rect.x, self.rect.y-10, filled_length, bar_height)
        pygame.draw.rect(screen, (140,0,0),filled_rect)                 
 
    def reset_position(self):
        plant_offset = random.randint(-5, 5)
        #self.rect.x = random.randint(0, width - self.rect.width)
        #self.rect.y = random.randint(0, height - self.rect.height)

        self.rect.x = max(0, min(self.rect.x + plant_offset, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y + plant_offset, height - self.rect.height))

    def add_energy(self, amount):
        #Increase but dont exceed max energy
        self.energy += amount
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def draw(self):
        if self.active:
           screen.blit(self.image, self.rect)
           self.draw_energy_bar()  
  
    def update(self, plants_list):
        current_time = time.time()
        if self.active and (current_time - self.last_division_time >= 25):  # 30 seconds
            self.divide(plants_list)
            self.last_division_time = current_time
            self.decay -= (cfg.PLANT_DECAY * random.random(0,1))


    def divide(self, plants_list):
        new_plant = Plant(self.energy)
        plants_list.append(new_plant)  # Add new plant to the list
    
    
class Predator:
    def __init__(self, 
                 energy = energy_pred, 
                 energy_efficiency=1.0):
        self.image = img_pred
        self.rect = self.image.get_rect()
        self.max_energy = energy_pred
        self.energy = energy
        self.active = True
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)

    def consume_cell(self, cell, current_time):
        if self.rect.colliderect(cell.rect) and cell.active:
            # Possibly add more logic here, e.g., energy transfer
            self.energy += cell.energy
            self.active = False
            #plant.regeneration_time = current_time + regeneration_delay
            return True
        return False

    def draw_energy_bar(self):
        bar_length = 20
        bar_height = 5
        energy_ratio = self.energy / self.max_energy
        energy_length = bar_length * bar_height
        #filled_length = int(self.energy /self.max_energy * bar_length)
        filled_length = int(energy_ratio * bar_length)
        bar_x = self.rect.centerx - bar_length // 2
        bar_y = self.rect.top - bar_height -5
        # Draw background of energy bar
        background_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_length, bar_height)
        pygame.draw.rect(screen, (0,0,0), background_rect)
        #Draw Current Energy Level
        filled_rect = pygame.Rect(self.rect.x, self.rect.y-10, filled_length, bar_height)
        pygame.draw.rect(screen, (140,0,0),filled_rect)
   
    def move(self):  # Ensure this method is correctly indented to be part of the Particle class
        # Simple movement logic: move the particle randomly
        self.rect.x += random.randint(-10, 10)
        self.rect.y += random.randint(-10, 10)
        # Keep the particle within the screen bounds
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))
        pass
    
    def divide(self, preds_list):
        if self.energy < cfg.DIVISION_THRESHOLD:
            self.divide(preds_list)
        self.energy = cfg.PREDATOR_ENERGY_INITIAL
        new_energy_eff = self.energy_efficiency # Parent keeps half its energy
        new_cell = Predator(self.energy * .75, new_energy_efficiency = self.energy_efficiency * np.random.normal(1, 0.05))  # Create a new cell with the same energy level

        # Slightly offset the new cell from the parent
        offset = random.randint(-2, 2)  # Adjust the offset value as needed
        new_cell.rect.x = max(0, min(self.rect.x + offset, width - new_cell.rect.width))
        new_cell.rect.y = max(0, min(self.rect.y + offset, height - new_cell.rect.height))

    def add_energy(self, amount):
        #Increase but dont exceed max energy
        self.energy += amount
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def draw(self):
        if self.energy >0:
            screen.blit(self.image, self.rect)
            self.draw_energy_bar()                 

    def update(self, cells, current_time):
        self.move()  # Predator moves in each update call
        self.energy -= cfg.PREDATOR_ENERGY_DECAY

        # Iterate through cells to check for collisions
        for cell in cells:
            if self.consume_cell(cell, current_time):
                # Handle the predator's energy increase or other effects here
                self.energy += cfg.ENERGY_GAIN_FROM_CELL  # Assuming this constant is defined in your configuration
                if self.energy > self.max_energy:
                    self.energy = self.max_energy
                cell.active = False  # Deactivate the cell after being consumed

### MUTATED CLASSES
                # Energy
                # Speed
                # Mutation Speed
class MutatedPredator(Cell):
    def __init__(self, 
                 energy=energy_start, 
                 energy_efficiency=1.0):
        super().__init__(energy, energy_efficiency)

    def consume(self, other_cell):
        pass

class MutatedCell(Cell):
    def __init__(self,
                 energy = energy_start * np.random.uniform(-1, 1),
                 energy_efficiency=1.0):
        super().__init__(energy,energy_efficiency=1.0)
    pass

class MutatedPlant(Plant):
    def __init__(self,
                energy = energy_start * np.random.uniform(-1, 1),
                energy_efficiency=1.0):
        super().__init__(energy,energy_efficiency=1.0)
    pass