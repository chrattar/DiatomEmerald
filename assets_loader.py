import pygame
import os

# Initialize Pygame
pygame.init()

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the path to the assets directory relative to the script location
assets_dir = os.path.join(script_dir, 'assets')

def load_image(name):
    # Construct the full path to the image using the relative assets directory
    path = os.path.join(assets_dir, name)
    return pygame.image.load(path).convert_alpha()

class AssetManager:
    def __init__(self):
        self.images = {
            'sprite1': load_image('sprite1.png'),
            'sprite2': load_image('sprite2.png'),
            'sprite3': load_image('sprite3.png'),
            #'sprite4': load_image('sprite4.png'), 

            # Add more images as needed
        }

    def get_image(self, name):
        return self.images.get(name)
