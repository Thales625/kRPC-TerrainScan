import pygame
from math import atan2, radians
from threading import Thread

from PyVecs import Vector2, Vector3

class Display:
    def __init__(self) -> None:
        self.screen_size = Vector2(600, 500)

        self.fov = radians(45)
        self.cam_pos = Vector3(0, -1.5, .5)

        self.vertices = []

        self.thread = Thread(target=self.loop)

        self.RUNNING = True

    def start(self):
        self.thread.start()

    def project(self, point_pos):
        point_dist_hor = (point_pos * Vector3(1, 1)).magnitude()

        point_angle_vert = atan2(point_pos.z, point_dist_hor)
        point_angle_hor = atan2(point_pos.x, point_pos.y)

        return (self.screen_size * 0.5) * Vector2(point_angle_hor/self.fov + 1, point_angle_vert/self.fov + 1)

    def update(self, matrix):
        # vertices[0] = (color, pos_2d)
        
        #vertices = [(tuple(Vector3(255, 255, 255) * (1 - p.magnitude() / max_dist)), p - self.cam_pos) for l in matrix for p in l]
        #vertices = [(tuple(Vector3(255, 255, 255) * max(0, min(1, 1-abs(p.z)))), p - self.cam_pos) for l in matrix for p in l]
        #vertices = [(tuple(Vector3(255, 255, 255) * (1 - (p - self.cam_pos).magnitude() / max_dist)), p - self.cam_pos) for l in matrix for p in l]
        vertices = [((255, 255, 255), p - self.cam_pos) for l in matrix for p in l]

        vertices.sort(key=lambda x: x[1].magnitude(), reverse=True)

        vertices = [(i[0], self.project(i[1])) for i in vertices]

        self.vertices = vertices

    def end(self):
        self.RUNNING = False

    def loop(self):
        pygame.init()
        self.screen = pygame.display.set_mode(tuple(self.screen_size))
        pygame.display.set_caption('Surface Lidar')

        while self.RUNNING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.RUNNING = False
                
            self.screen.fill((52, 53, 65)) # Clear Screen

            for (color, pos) in self.vertices:
                pygame.draw.circle(self.screen, color, tuple(pos), 2)

            pygame.display.update() # Update Screen
