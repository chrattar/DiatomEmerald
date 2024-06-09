import pygame
import random
import sys
import config as cfg
import pandas as pandas
import matplotlib.pyplot as plt
import threading
from assets_loader import AssetManager
import time

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

#Display
width, height = cfg.WIDTH, cfg.HEIGHT
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Particle Simulation")
regeneration_delay = cfg.REGENERATION_DELAY

#Assets - pulled from assets_loader.py
assets = AssetManager()
energy_start = cfg.ENERGY_INITIAL
energy_cell_max = cfg.ENERGY_MAX_CELL
energy_plant = cfg.ENERGY_PLANT
energy_pred = cfg. ENERGY_INITIAL_PREDATOR
#sprite_image = pygame.image.load('sprite.png').convert_alpha() For local load
cell_image = assets.get_image('sprite1')
plant_image = assets.get_image('sprite2')
pred_image = assets.get_image('sprite3')

#LOGGING
last_log_time = time.time()
log_interval = 1
counts_log = []

def draw_text(screen, text, position, font, color=(255,255,255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Particle class definitions
class Cell:
    def __init__(self, energy=energy_start):
        self.image = cell_image
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
    
    def cell_mutation(self):
        pass


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
        self.energy -= cfg.ENERGY_DECAY  # Energy decay over time

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
    def __init__(self):
        self.image = plant_image
        self.rect = self.image.get_rect()
        self.active = True
        #self.reset_position()
        #below would manually set position. ResetPosition is doing this for me right now
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(0, height - self.rect.height)
        self.energy = energy_plant  # Fixed amount of energy the plant provides
        self.regeneration_time = 0
    
    def reset_position(self):
        plant_offset = random.randint(-5, 5)
        #self.rect.x = random.randint(0, width - self.rect.width)
        #self.rect.y = random.randint(0, height - self.rect.height)

        self.rect.x = max(0, min(self.rect.x + plant_offset, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y + plant_offset, height - self.rect.height))
    
    def draw(self):
        if self.active:
           screen.blit(self.image, self.rect)

class Predator:
    def __init__(self, energy = energy_pred):
        self.image = pred_image
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
        self.energy = cfg.ENERGY_INITIAL_PREDATOR  # Parent keeps half its energy
        new_cell = Predator(self.energy)  # Create a new cell with the same energy level

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
        self.energy -= cfg.ENERGY_DECAY_PREDATOR

        # Iterate through cells to check for collisions
        for cell in cells:
            if self.consume_cell(cell, current_time):
                # Handle the predator's energy increase or other effects here
                self.energy += cfg.ENERGY_GAIN_FROM_CELL  # Assuming this constant is defined in your configuration
                if self.energy > self.max_energy:
                    self.energy = self.max_energy
                cell.active = False  # Deactivate the cell after being consumed


def main():
    clock = pygame.time.Clock()
    cells = [Cell() for _ in range(cfg.NUM_CELLS)]  # Create NUM_PARTICLES particles count
    plants = [Plant() for _ in range(cfg.NUM_PLANTS)] # Create NUM_PLANTS
    preds = [Predator() for _ in range(cfg.NUM_PREDATORS)]
    last_update = pygame.time.get_ticks()
    is_paused = False  # Initialize is_paused outside the loop


    while True:
        #current_time = pygame.time.get_ticks()
        current_time = time.time()
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
                        plant.active = False  # Ensure this method checks plant's active status
                        # Handle plant consumption logic here (e.g., deactivate plant, increase cell energy)
                        #cell.draw()
                        
               # for plant in plants:  #    plant.draw()#   if not plant.active and current_time - plant.regeneration_time >= 0:#      plant.reset_position()#     plant.active = True

            for plant in plants:
                plant.draw()
                if not plant.active and current_time - plant.regeneration_time >= 0:
                    plant.reset_position()
                    plant.active = True

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

        if current_time - last_log_time >= log_interval:
            active_cells_count = sum(1 for cell in cells if cell.energy > 0)
            active_plants_count = sum(1 for plant in plants if plant.active)
            active_preds_count = sum(1 for pred in preds if pred.energy > 0)

            counts_log.append({
                'time':current_time,
                'active_cells': active_cells_count,
                'active_plants':active_plants_count,
                'active_preds': active_preds_count

            })


        pygame.display.flip()  # Update the display once per loop iteration
        clock.tick(30)  # Control the frame rate

        if not is_paused:
            cells = [p for p in cells if p.energy > 0]  # Remove cells with no energy outside of pause


if __name__ == "__main__":
    main()


    times = [entry['time']/1000 for entry in counts_log]
    active_cells = [entry['active_cells'] for entry in counts_log]
    active_plants = [entry['active_plants'] for entry in counts_log]
    active_preds = [entry['active_preds'] for entry in counts_log]

    plt.figure(figsize=(10,6))
    plt.plot(times, active_cells, label='Active Cells')
    plt.plot(times, active_plants, label='Active Plants')
    plt.plot(times, active_preds, label='Active Predators')
    plt.xlabel('Time (s)')
    plt.ylabel('Count')
    plt.title('Counts Over Time')
    plt.legend()
    plt.show()

