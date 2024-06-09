#SETTINGS

#Display Settings
WIDTH = 1920
HEIGHT = 1080
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
SIZE_RANGE = (5, 15)  # Min and max size of particles
SHAPES = ['circle', 'square']  # Available shapes

#Entity Variables

#Evolution settings
MUTATION_RATE = 1
REGENERATION_DELAY = 5000
DIVISION_THRESHOLD = 550 #costs the cell 50 energy to split

#CELL VARIABLES
CELLS_NUM = 40 # Number of particles in the simulation
ENERGY_INITIAL = 400
CELL_ENERGY_MAX = 1000
CELL_ENERGY_DECAY = 1
ENERGY_GAIN_FROM_CELL = 200

#PLANT VARIABLES
PLANTS_NUM = 100
PLANTS_ENERGY = 50
PLANTS_ENERGY_MAX = 50
PLANT_ENERGY_GROWTH = -1
PLANT_GROWTH_THRESHOLD = 20
PLANT_DECAY = 0


#PREDATOR VARIABLES
PREDATORS_NUM = 10
PREDATOR_ENERGY_DECAY = 5
PREDATOR_ENERGY_INITAL = 600


#Environment Settings
temp_env = 22





