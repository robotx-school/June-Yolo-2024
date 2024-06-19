import urx
#from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper
import os
import time
import numpy as np
import math3d as m3d
import math
import socketio

def get_robot_cords(x_y):
    robot_coords = []
    x, y = x_y[0], x_y[1]
    y_r = x - 325
    x_r = y - 450
    robot_coords.append(x_r / 1000)
    robot_coords.append(y_r / 1000)
    return robot_coords




# Класс для управления подменным (заглушкой) роботом
class Nedorobot:
    def __init__(self, ip):
        self.ip = ip  # Иkиализация IP-адреса робота

    def getl(self):
        print('Nedorobot_ok')  # Метод для вывода состояния робота-заглушки

    def movel(self, coord, a, b, wait='0'):
        print('Go to', self.ip, coord)  # Метод для имитации перемещения робота-заглушки


# Класс для управления подменным гриппером
class Nedogripper:
    def __init__(self, robot_id):
        print('Nedogripper_ok')  # Выводит сообщение при создании экземпляра класса

    def gripper_action(self, angle):
        print('Gripper goto', angle)  # Метод для имитации действия гриппера




class XGripper:
    def __init__(self, server_url="http://192.168.1.3:8989"):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.setup_events()

    def setup_events(self):
        @self.sio.event
        def connect():
            print('Connected to server')

        @self.sio.event
        def disconnect():
            print('Disconnected from server')

    def connect(self):
        try:
            self.sio.connect(self.server_url)
        except socketio.exceptions.ConnectionError as e:
            print(f"ConnectionError: {e}")

    def disconnect(self):
        self.sio.disconnect()

    def gripper_action(self, angle, servo_delay=30, current=250, wait=True):
        command = f"{angle};{servo_delay};{current}"
        self.sio.emit('send_command', command)
        print(f"Command sent: {command}")
        if wait:
            time.sleep(0.5)


try:
    robot = urx.Robot('192.168.1.2')  # Попытка подключения к реальному роботу
    print("robot is OK")
except Exception as e:
    robot = Nedorobot('robot')  # Использование робота-заглушки при ошибке
    print('Robot is Nedorobot', e)  # Вывод ошибки

try:
    grip = gripper = XGripper('http://192.168.1.3:8989')
    gripper.connect()
    print('Gripper is XGripper')
except Exception as e:
    grip = Nedogripper(robot)  # Использование гриппера-заглушки при ошибке
    print('Gripper is Nedogripper', e)  # Вывод ошибки

state = robot.getl()  # Получение состояния робота
print(state)  # Вывод состояния робота

# Словарь с предопределенными позициями робота
robot_positions = {'work_pos': [-0.233, 0.09, 0.26, 90],
                   'home_pos': [-0.100, 0.106, 0.250, 90],
                   'left_pos': [*get_robot_cords((150,150)),0.15,90],
                   'right_pos': [*get_robot_cords((550,550)),0.15,90],
                   'left_1st_pos': [*get_robot_cords((25, 275)), 0.15, 90],
                   'left_2nd_pos': [*get_robot_cords((25, 475)), 0.15, 90],
                   'right_1st_pos': [*get_robot_cords((575, 475)), 0.15, 90],

                   'low_left_1st_pos': [*get_robot_cords((25, 275)), 0.06, 90],
                   'low_left_2nd_pos': [*get_robot_cords((25, 475)), 0.06, 90],
                   'low_right_1st_pos': [*get_robot_cords((575, 475)), 0.06, 90],
                   }


# Функция для расчета угловых координат гриппера
def angle_gripper(angle):
    # Преобразование угла для использования в матрицах поворота
    angle = 45 - angle - 0.01
    roll = 0
    pitch = 3.14
    yaw = np.deg2rad(angle)

    # Создание матриц поворота по трем осям
    yawMatrix = np.matrix([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]
    ])

    pitchMatrix = np.matrix([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
    ])

    rollMatrix = np.matrix([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
    ])

    # Комбинирование матриц для получения конечной матрицы поворота
    R = yawMatrix * pitchMatrix * rollMatrix

    # Расчет углов Эйлера из матрицы поворота
    theta = math.acos(((R[0, 0] + R[1, 1] + R[2, 2]) - 1) / 2)
    multi = 1 / (2 * math.sin(theta))

    rx = multi * (R[2, 1] - R[1, 2]) * theta
    ry = multi * (R[0, 2] - R[2, 0]) * theta
    rz = multi * (R[1, 0] - R[0, 1]) * theta
    rz = 0

    return rx, ry, rz


# Функция для преобразования координат в систему координат робота


# Функция для управления движением робота
def move_robot(x, y, z, angle, w=True):
    distance = (x ** 2 + y ** 2 + z ** 2) ** 0.5
    print(f"Go to:{x},{y},{z}, Distance = {round(distance, 2)}")
    if not 0.2 < distance < 0.5:
        print("wrong distance. Point unreacheble")
    if not 0 <= angle <= 135:
        print("Wrong gripper angle")
        robot.stop()
        os._exit(0)
    if not 0.01 <= z <= 0.29:
        print(f"Wrong Z-position: {z}")
        robot.stop()
        os._exit(0)
    if not -0.3 <= y <= 0.3:
        print(f"Wrong X-position: {y}")
        robot.stop()
        os._exit(0)
    if not -0.4 <= x <= 0.1:
        print(f"Wrong Y-position: {x}")
        robot.stop()
        os._exit(0)
    rx, ry, rz = angle_gripper(angle)  # Получение угловых координат для гриппера
    robot.movel([x, y, z, rx, ry, rz], 0.50, 0.50, wait=w)  # Команда на перемещение робота
