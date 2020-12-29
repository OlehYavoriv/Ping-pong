from socket import socket, AF_INET, SOCK_STREAM
from sys import argv
from threading import Thread
import pickle
import struct

import pygame as pg

from enum import IntEnum


WindowPosition = IntEnum("WindowPosition", "LEFT MIDDLE RIGHT")
Keys = IntEnum("Keys", "UP DOWN LEFT RIGHT SPACE S")


class PongClient:
    def __init__(self, host="0.0.0.0", port=5555):
        self.tcpsocket = socket(AF_INET, SOCK_STREAM)
        self.tcpsocket.connect((host, port))
        self.game_state = None

        settings = self.get_settings()
        self.window_position = WindowPosition(settings["window_position"])
        self.resolution = settings["resolution"]

        Thread(target=self.get_game_state, daemon=True).start()

    def key_pressed(self, key):
        key = str(key).encode()
        data = struct.pack('i', len(key)) + key
        self.tcpsocket.sendall(data)

    def get_settings(self):
        return pickle.loads(self.tcpsocket.recv(1024))

    def get_game_state(self):
        while True:
            size = struct.unpack("i", self.tcpsocket.recv(struct.calcsize("i")))[0]
            data = b""
            while len(data) < size:
                piece = self.tcpsocket.recv(size - len(data))
                data += piece
            self.game_state = pickle.loads(data)


host = None
port = None


if (l := len(argv)) > 1:
    host = argv[1]
elif l > 2:
    try:
        port = int(argv[2])
    except ValueError:
        print("Port must be a number")
        exit()

pongGame = None
if host is not None and port is not None:
    pongGame = PongClient(host, port)
elif host is not None:
    pongGame = PongClient(host)
elif port is not None:
    pongGame = PongClient(port=port)
else:
    pongGame = PongClient()


pg.init()
screen = pg.display.set_mode(pongGame.resolution)
pg.display.set_caption("Ping-Pong")

clock = pg.time.Clock()
running = True
while running:
    clock.tick(60)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                pongGame.key_pressed(Keys.SPACE.value)
            elif event.key == pg.K_s:
                pongGame.key_pressed(Keys.S.value)

    key = pg.key.get_pressed()
    if key[pg.K_UP]:
        pongGame.key_pressed(Keys.UP.value)
    elif key[pg.K_DOWN]:
        pongGame.key_pressed(Keys.DOWN.value)
    elif key[pg.K_LEFT]:
        pongGame.key_pressed(Keys.LEFT.value)
    elif key[pg.K_RIGHT]:
        pongGame.key_pressed(Keys.RIGHT.value)

    screen.fill((0,165,16))

    if pongGame.game_state is not None:
        ball_position = pongGame.game_state["ball_position"]

        if pongGame.window_position == WindowPosition.LEFT:
            pg.draw.rect(screen, (255, 255, 0), pongGame.game_state["left_paddle"])
            pg.draw.circle(screen, (255,255,255), (int(ball_position[0]), int(ball_position[1])), 5)
            y = pongGame.resolution[0] * 0.10 + 10 
            line_height = pongGame.resolution[1] / 15
            space = pongGame.resolution[1] / 30
            pg.draw.line(screen, (255, 255, 255),(y, 15 * line_height),(y, 0 * line_height ), 2)

        elif pongGame.window_position == WindowPosition.MIDDLE:
            x = pongGame.resolution[0] / 2 - 2.5
            line_height = pongGame.resolution[1] / 15
            space = pongGame.resolution[1] / 30
            pg.draw.line(screen, (255, 255, 255),(x, 15 * line_height),(x, 0 * line_height ), 2)

            pg.draw.circle(screen, (255, 255, 255), (int(ball_position[0] - 350), int(ball_position[1])), 5)
        elif pongGame.window_position == WindowPosition.RIGHT:
            paddle_position = list(pongGame.game_state["right_paddle"])
            paddle_position[0] -= 700
            pg.draw.rect(screen, (255, 255, 0), paddle_position)
            z = pongGame.resolution[0] * 0.86 + 5
            line_height = pongGame.resolution[1] / 15
            space = pongGame.resolution[1] / 30
            pg.draw.line(screen, (255, 255, 255),(z, 15 * line_height),(z, 0 * line_height ),2)
            pg.draw.circle(screen, (255,255,255), (int(ball_position[0] - 700), int(ball_position[1])), 5)

    pg.display.flip()
pg.quit()
