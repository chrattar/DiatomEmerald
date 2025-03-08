import pygame
import random
import sys
import config as cfg
import threading
from assets_loader import AssetManager
import time

class Slider:
    def __init__(self, x, y, width, height, initial_value=0, min_value=0, max_value=100, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        self.font = pygame.font.SysFont('Consolas', 24)
        self.active = False  # To track if this slider is currently active for keyboard input

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        handle_rect = pygame.Rect(self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width - 10, self.rect.y, 20, self.rect.height)
        pygame.draw.rect(screen, (100, 100, 100), handle_rect)
        # Draw the label
        label_surface = self.font.render(f"{self.label}: {int(self.value)}", True, (255, 255, 255))
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
        elif event.type == pygame.MOUSEMOTION and self.active:
            rel_x = event.pos[0] - self.rect.x
            self.value = (rel_x / self.rect.width) * (self.max_value - self.min_value) + self.min_value
            self.value = min(max(self.value, self.min_value), self.max_value)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RIGHT:
                self.value = min(self.value + 1, self.max_value)
            elif event.key == pygame.K_LEFT:
                self.value = max(self.value - 1, self.min_value)
            elif event.key == pygame.K_UP:
                self.value = min(self.value + 10, self.max_value)
            elif event.key == pygame.K_DOWN:
                self.value = max(self.value - 10, self.min_value)

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
