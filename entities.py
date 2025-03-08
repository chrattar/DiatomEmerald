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
#Sprties
img_cell = assets.get_image('sprite1')
img_omni = assets.get_image('sprite4')
img_plant = assets.get_image('sprite2')
img_pred = assets.get_image('sprite3')

#CLASSES
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
        self.energy = cfg.ENERGY_INITIAL
        new_cell = Cell(self.energy)
        offset = random.randint(-2, 2) 
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
            #print(f"Plant consumed by cell at {self.rect.topleft}")
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
        current_time = time.time()
        if self.energy <= 0:
            return 
        self.move()
        self.energy -= cfg.CELL_ENERGY_DECAY

        while self.energy >= cfg.DIVISION_THRESHOLD:
            self.divide(cells_list)
        
        if random.random() < cfg.MUTATION_TO_OMNIVORE_RATE:
            new_omnivore = Omnivore(energy=self.energy, parent_type='cell')
            return new_omnivore
        return None
        
    def move(self):  
        # Simple movement logic: move the particle randomly
        self.rect.x += random.randint(-10, 10)
        self.rect.y += random.randint(-10, 10)
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))
        pass

class Plant:
    def __init__(self, energy=energy_plant, energy_efficiency=1.0):
        self.image = img_plant
        self.rect = self.image.get_rect()
        self.active = True
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)
        self.energy = min(energy, energy_plant_max)  # Ensure initial energy doesn't exceed max
        self.max_energy = energy_plant_max
        self.regeneration_time = 0
        self.last_division_time = time.time()
        self.division_cooldown = 5  # Time in seconds between divisions
        self.energy_decay_rate = cfg.PLANT_DECAY

    def draw_energy_bar(self):
        bar_length = 20
        bar_height = 5
        energy_ratio = max(0, min(self.energy / self.max_energy, 1))  # Clamp between 0 and 1
        filled_length = int(energy_ratio * bar_length)
        
        # Draw background
        background_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_length, bar_height)
        pygame.draw.rect(screen, (0, 0, 0), background_rect)
        
        # Draw energy level
        if filled_length > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y - 10, filled_length, bar_height)
            pygame.draw.rect(screen, (140, 0, 0), filled_rect)

    def reset_position(self):
        plant_offset = random.randint(-5, 5)
        self.rect.x = max(0, min(self.rect.x + plant_offset, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y + plant_offset, height - self.rect.height))

    def add_energy(self, amount):
        self.energy = min(self.energy + amount, self.max_energy)

    def draw(self):
        if self.active:
            screen.blit(self.image, self.rect)
            self.draw_energy_bar()

    def update(self, plants_list):
        if not self.active:
            return
        current_time = time.time()
        decay_amount = self.energy_decay_rate * random.uniform(0, 1)
        self.energy = max(0, self.energy - decay_amount)
        
        #PLANT IS DEAD y/n
        if self.energy <= 0:
            self.active = False
            return
            
        # Handle division
        if current_time - self.last_division_time >= self.division_cooldown:
            if self.energy >= self.max_energy * 0.5:  # Only divide if enough energy
                self.divide(plants_list)
                self.last_division_time = current_time

    def divide(self, plants_list):
        split_energy = self.energy * 0.5
        self.energy = split_energy
        new_plant = Plant(energy=split_energy)
        new_plant.rect.x = max(0, min(self.rect.x + random.randint(-20, 20), width - new_plant.rect.width))
        new_plant.rect.y = max(0, min(self.rect.y + random.randint(-20, 20), height - new_plant.rect.height))
        plants_list.append(new_plant)
    
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
        self.last_division_time = 0

    def consume_cell(self, cell, current_time):
        if self.rect.colliderect(cell.rect) and cell.active:
            # Possibly add more logic here, e.g., energy transfer
            self.energy += cell.energy
            print(f"Pred -- Energy after: {self.energy}")
            cell.active = False
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
   
    def move(self):  
        self.rect.x += random.randint(-10, 10)
        self.rect.y += random.randint(-10, 10)
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))        # Keep inside scren
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))        # Keep inside scren
        pass
    
    def divide(self, preds_list, current_time):
        division_cooldown = 3000
        print(f"Energy: {self.energy}, Lower: {cfg.PREDATOR_DIVISION_THRESHOLD_LOWER}, Upper: {cfg.PREDATOR_DIVISION_THRESHOLD_UPPER}")
        print(f"Time diff: {current_time - self.last_division_time}, Cooldown: {division_cooldown}")
        if (self.energy <= cfg.PREDATOR_DIVISION_THRESHOLD_UPPER and 
                self.energy >= cfg.PREDATOR_DIVISION_THRESHOLD_LOWER and
                current_time - self.last_division_time > division_cooldown):
                self.energy *= 0.25  # Parent keeps 25%
                new_pred = Predator(self.energy * 3)  # Child gets 75%
                print(f"DIVISION TRIGGERED! Energy: {self.energy}")
                offset = random.randint(-2, 2)
                new_pred.rect.x = max(0, min(self.rect.x + offset, cfg.WIDTH - new_pred.rect.width))
                new_pred.rect.y = max(0, min(self.rect.y + offset, cfg.HEIGHT - new_pred.rect.height))         
                preds_list.append(new_pred)
                self.last_division_time = current_time

    def add_energy(self, amount):
        #Increase but dont exceed max energy
        self.energy += amount
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def draw(self):
        if self.energy >0:
            screen.blit(self.image, self.rect)
            self.draw_energy_bar()                 

    def update(self, cells, current_time, preds_list):
        self.move()  # Predator moves in each update call
        self.energy -= cfg.PREDATOR_ENERGY_DECAY
        self.divide(preds_list,current_time)

        for cell in cells:
            if self.consume_cell(cell, current_time):
                # Handle the predator's energy increase or other effects here
                self.energy += cfg.ENERGY_GAIN_FROM_CELL  # Assuming this constant is defined in your configuration
                if self.energy > self.max_energy:
                    self.energy = self.max_energy
                cell.active = False  # Deactivate the cell after being consumed

        if random.random() < cfg.MUTATION_TO_OMNIVORE_RATE:
            new_omnivore = Omnivore(energy=self.energy, parent_type='predator')
            return new_omnivore
        return None
    
class Omnivore:
    def __init__(self, energy=energy_pred, energy_efficiency=1.0, parent_type = None):
        self.image = img_omni  # You'll need to add a specific omnivore image
        self.rect = self.image.get_rect()
        self.max_energy = energy_pred
        self.energy = energy
        self.active = True
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)
        self.parent_type = parent_type

    def consume(self, target, current_time):
        if self.rect.colliderect(target.rect) and target.active:
            gained_energy = cfg.OMNIVORE_ENERGY_GAIN_CELL if isinstance(target, Cell) else cfg.OMNIVORE_ENERGY_GAIN_PLANT
            self.energy += gained_energy
            target.active = False
            return True
        return False

    def draw_energy_bar(self):
        bar_length = 20
        bar_height = 5
        energy_ratio = self.energy / self.max_energy
        filled_length = int(energy_ratio * bar_length)  
        background_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_length, bar_height)
        pygame.draw.rect(screen, (0,0,0), background_rect)
        
        filled_rect = pygame.Rect(self.rect.x, self.rect.y-10, filled_length, bar_height)
        pygame.draw.rect(screen, (140,0,0), filled_rect)

    def move(self):
        self.rect.x += random.randint(-10, 10)
        self.rect.y += random.randint(-10, 10)
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))

    def divide(self, omnis_list):
        if self.energy > cfg.DIVISION_THRESHOLD:
            new_omnivore = Omnivore(self.energy * 0.5)
            offset = random.randint(-2, 2)
            new_omnivore.rect.x = max(0, min(self.rect.x + offset, width - new_omnivore.rect.width))
            new_omnivore.rect.y = max(0, min(self.rect.y + offset, height - new_omnivore.rect.height))
            omnis_list.append(new_omnivore)
            self.energy *= 0.5

    def add_energy(self, amount):
        self.energy = min(self.energy + amount, self.max_energy)

    def draw(self):
        if self.energy > 0:
            screen.blit(self.image, self.rect)
            self.draw_energy_bar()

    def update(self, cells, plants, omnis_list, current_time):
        if self.energy <= 0:
            return

        self.move()
        self.energy -= cfg.OMNIVORE_ENERGY_DECAY

        # Check for food (both cells and plants)
        for cell in cells[:]:  # Use slice to avoid modification during iteration
            if self.consume(cell, current_time):
                cell.active = False

        for plant in plants[:]:  # Use slice to avoid modification during iteration
            if self.consume(plant, current_time):
                plant.active = False

        # Check for division
        if self.energy > cfg.DIVISION_THRESHOLD:
            self.divide(omnis_list)

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