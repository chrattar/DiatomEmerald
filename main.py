import sys
import pygame

import config as cfg
from assets_loader import AssetManager
from entities import Cell, Predator, Plant
from entities_config import Slider

# Initialize Pygame and the screen
def init_pygame():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Particle Simulation")
    return screen

# Utility function to draw text
def draw_text(screen, text, position, font_name, size=20, color=(255, 255, 255)):
    font = pygame.font.SysFont(font_name, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Utility function to draw a button
def draw_button(screen, text, rect, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button = pygame.Rect(rect)

    if button.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, button)
        if click[0] == 1 and action:
            pygame.time.wait(200)  # Prevent multiple clicks
            action()
    else:
        pygame.draw.rect(screen, color, button)

    text_surf = pygame.font.SysFont("Verdana", 20).render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=button.center)
    screen.blit(text_surf, text_rect)

def draw_selection_screen(screen, settings):
    screen.fill((50, 50, 50))  # Dark grey background
    font = pygame.font.SysFont('Consolas', 24)
    offset = 50
    sliders = []

    for key, value in settings.items():
        # Draw text for each setting
        label = font.render(f'{key}: {value}', True, (255, 255, 255))
        screen.blit(label, (50, offset))

        # Create Sliders for Numeric Values
        slider = Slider(300, 
                        offset, 
                        600, 
                        20, 
                        initial_value=value, 
                        min_value=0, 
                        max_value=1000, 
                        label=key)
        sliders.append(slider)
        slider.draw(screen)
        offset += 70

    return sliders

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        return event

def start_screen(screen):
    running = True
    while running:
        event = handle_events()
        if event is None:
            continue
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            running = False
            selection_screen(screen)

        screen.fill((0, 0, 0))
        draw_text(screen, "Press SPACE to start or ESC to exit", (50, 50), "Verdana", 30)
        pygame.display.flip()
        pygame.time.Clock().tick(30)

def selection_screen(screen):
    settings = {
        'CELLS COUNT': cfg.CELLS_NUM,
        'PLANT COUNT': cfg.PLANTS_NUM,
        'PREDATOR COUNT': cfg.PREDATORS_NUM
    }
    sliders = draw_selection_screen(screen, settings)
    running = True

    while running:
        screen.fill((50, 50, 50))  # Dark grey background
        for slider in sliders:
            slider.draw(screen)

        event = handle_events()
        if event is None:
            continue
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            for slider in sliders:
                settings[slider.label] = int(slider.get_value())
            update_config(settings)
            running = False

        for slider in sliders:
            slider.handle_event(event)

        pygame.display.flip()

def update_config(settings):
    cfg.CELLS_NUM = settings['CELLS COUNT']
    cfg.PLANTS_NUM = settings['PLANT COUNT']
    cfg.PREDATORS_NUM = settings['PREDATOR COUNT']

def main_loop(screen):
    clock = pygame.time.Clock()
    cells = [Cell() for _ in range(cfg.CELLS_NUM)]
    plants = [Plant() for _ in range(cfg.PLANTS_NUM)]
    preds = [Predator() for _ in range(cfg.PREDATORS_NUM)]
    is_paused = False

    while True:
        event = handle_events()
        if event is None:
            continue
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            is_paused = not is_paused

        if not is_paused:
            screen.fill((0, 90, 90))
            update_entities(cells, plants, preds)
            draw_entities(screen, cells, plants, preds)
        else:
            draw_text(screen, "Paused", (600, 400), "Verdana", 30, (255, 0, 0))

        pygame.display.flip()
        clock.tick(30)

def update_entities(cells, plants, preds):
    current_time = pygame.time.get_ticks()
    for pred in preds:
        pred.update(cells, current_time)
    for cell in cells:
        cell.update(cells)
        for plant in plants:
            if cell.consume_plant(plant, current_time):
                plant.active = False
                plant.regeneration_time = current_time + cfg.REGENERATION_DELAY
    for plant in plants:
        plant.update(plants)
        if not plant.active and current_time >= plant.regeneration_time:
            plant.reset_position()
            plant.active = True

def draw_entities(screen, cells, plants, preds):
    for pred in preds:
        pred.draw()
    for cell in cells:
        cell.draw()
    for plant in plants:
        plant.draw()
    draw_counts(screen, cells, plants, preds)

def draw_counts(screen, cells, plants, preds):
    active_cells_count = sum(1 for cell in cells if cell.energy > 0)
    active_plants_count = sum(1 for plant in plants if plant.active)
    active_preds_count = sum(1 for pred in preds if pred.energy > 0)
    draw_text(screen, f"Cells: {active_cells_count}", (10, 10), "Verdana", color=(0, 255, 255))
    draw_text(screen, f"Plants: {active_plants_count}", (10, 40), "Verdana", color=(0, 255, 0))
    draw_text(screen, f"Preds: {active_preds_count}", (10, 70), "Verdana", color=(255, 0, 0))

if __name__ == "__main__":
    screen = init_pygame()
    start_screen(screen)
    selection_screen(screen)
    main_loop(screen)
