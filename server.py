from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
import pickle
import struct

from pongEngine import PongGameEngine
from enum import IntEnum


WindowPosition = IntEnum("WindowPosition", "LEFT MIDDLE RIGHT")
Keys = IntEnum("Keys", "UP DOWN LEFT RIGHT SPACE S")


class PongServer:
    def __init__(self, host="0.0.0.0", port=5555, one_window_size=(350,350)):
        self.one_window_size = one_window_size
        self.tcpsocket = socket(AF_INET, SOCK_STREAM)
        self.tcpsocket.bind((host, port))
        self.tcpsocket.listen(3)

        self.connections = []

        self.pong_engine = PongGameEngine((one_window_size[0] * 3, one_window_size[1]))

        def update_pong_game():
            while True:
                sleep(1 / 60)
                self.pong_engine.update()
        Thread(target=update_pong_game, daemon=True).start()
        self.run()

    def accept_connections(self):
        for i in range(1, 3 + 1):
            conn, _ = self.tcpsocket.accept()
            settings = {}
            settings["window_position"] = i
            settings["resolution"] = self.one_window_size
            conn.sendall(pickle.dumps(settings, -1))
            self.connections.append(conn)

            Thread(target=self.key_handler, args=(conn, WindowPosition(i)), daemon=True).start()

    def run(self):
        self.accept_connections()
        while True:
            sleep(1 / 60)
            game_state = pickle.dumps(self.game_state, -1)
            data = struct.pack('i', len(game_state)) + game_state
            for conn in self.connections:
                conn.sendall(data)

    def key_handler(self, connection, position):
        while True:
            size = struct.unpack("i", connection.recv(struct.calcsize("i")))[0]
            data = b""
            while len(data) < size:
                piece = connection.recv(size - len(data))
                data += piece
            key = Keys(int(data.decode()))

            if position == WindowPosition.LEFT:
                if key == Keys.UP:
                    self.pong_engine.left_paddle.moveUp()
                if key == Keys.DOWN:
                    self.pong_engine.left_paddle.moveDown()
            elif position == WindowPosition.RIGHT:
                if key == Keys.UP:
                    self.pong_engine.right_paddle.moveUp()
                if key == Keys.DOWN:
                    self.pong_engine.right_paddle.moveDown()

            if key == Keys.SPACE:
                self.pong_engine.restart()
            elif key == Keys.S:
                self.pong_engine.ball.shoot()

    @property
    def game_state(self):
        data = {}
        data["ball_position"] = self.pong_engine.ball.position
        data["left_paddle"] = (
            *self.pong_engine.left_paddle.position,
            self.pong_engine.left_paddle.width,
            self.pong_engine.left_paddle.height
        )

        data["right_paddle"] = (
            *self.pong_engine.right_paddle.position,
            self.pong_engine.right_paddle.width,
            self.pong_engine.right_paddle.height
        )
        data["score"] = self.pong_engine.score
        return data

    def close(self):
        self.tcpsocket.close()


if __name__ == "__main__":
    PongServer()
