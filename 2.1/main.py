import cv2
import numpy as np
import time
from robot_control import *
import keyboard
import threading
import os
from collections import defaultdict
from ultralytics import YOLO
from warp_field import warp_field
from wait_for_cube import check_cube
from predict_position import predict_position
from FPS import Fps
model = YOLO("best2.pt")
counter_moving = {"blue":0,"red":0,"purple":0}
move_coord = [175,200]

def take_photo():
    pass
# Функция, определяющая задачи для робота

def go_to_1st_left_from_center():
    move_robot(*robot_positions['work_pos'])
    move_robot(*robot_positions['left_pos'])
    move_robot(*robot_positions['left_1st_pos'])
    move_robot(*robot_positions['low_left_1st_pos'])


def go_to_2nd_left_from_center():
    move_robot(*robot_positions['work_pos'])
    move_robot(*robot_positions['left_pos'])
    move_robot(*robot_positions['left_1st_pos'])
    move_robot(*robot_positions['left_2nd_pos'])
    move_robot(*robot_positions['low_left_2nd_pos'])

def go_to_right_from_center():
    move_robot(*robot_positions['work_pos'])
    move_robot(*robot_positions['right_pos'])
    move_robot(*robot_positions['right_1st_pos'])
    move_robot(*robot_positions['low_right_1st_pos'])

def go_to_center_from_left():
    move_robot(*robot_positions['left_1st_pos'])
    move_robot(*robot_positions['left_pos'])
    move_robot(*robot_positions['work_pos'])


def robot_task():
    global move_coord
    move_robot(*robot_positions["work_pos"])
    move_robot(*get_robot_cords(move_coord),0.22,0)

    #move_robot(*get_robot_cords(move_coord),0.22,0)
    grip.gripper_action(0,servo_delay = 20)
    move_robot(*get_robot_cords(move_coord),0.25,90)
    move_robot(*get_robot_cords([300,50]),0.25,90)
    grip.gripper_action(50,servo_delay = 20)



    """
    move_robot(*robot_positions['work_pos'])
    move_robot(*robot_positions['home_pos'])
    if keyboard.is_pressed('shift')
    a = int(input())
    [go_to_1st_left_from_center,
    go_to_2nd_left_from_center,
    go_to_right_from_center][a]()

    x_r, y_r = get_robot_cords((350, 150))
    #move_robot(x_r, y_r, 0.12, 90)
    
            
    
    time.sleep(30)
    
    os._exit(0)  # Завершение процесса
    """
    #wait_for_cube()

def control_camera():
    fps = 0
    fps_start_time = 0
    fps_counter = 0
    while 1:
        global cap
        OK, frame = cap.read()
        
        
        #print("FPS:",Fps())
        if not OK:
            print("Error image hasn't been read")
            os._exit(0)
            time.sleep(0.01)
        print("image read OK:")
        cv2.imshow("leoniding machin", frame)
        frame = cv2.resize(frame, (640,480))
        frame = warp_field(frame,dictionary)
        predict_list, track, coords_list, counter_moving,vis = check_cube(frame,fps)
        #out_list = check_cube(frame,fps)
      
        """
        if out_list is not None:
            for i in range(len(out_list[0])):
                coo_list = ["ShebaCube","ivanCube","SUSCube"]
                try:
                    future_x = out_list[0][coo_list[i]][0]
                    future_y = out_list[0][coo_list[i]][1]
                    print("Y:",future_y)
                    print("X:",future_x)
                    #print("real y:",out_list[2])
                    if 230 <= future_y <= 380 and 320 <= future_x <= 370 and 230 <= out_list[2]["ivanCube"][1] <= 380:
                        print("AIAIAIAIAIAIAIAIAIAIAI")
                        if i == 1:
                            print(f"MOOVE MANIPULATOR TO X: {future_x}; Y: {future_y} in 1 second")
                except Exception as e:
            
                    print(e)


            cv2.imshow("leoniding machin(bulochka s sosiskou)", out_list[4])
        """
        print(predict_list["ivanCube"])
        if predict_list["ivanCube"] != [] and coords_list["ivanCube"] != [] and predict_list["ivanCube"] is not None:
            if(170 <= predict_list["ivanCube"][1] <= 270 and 180 <= predict_list["ivanCube"][0] <= 230 and 170 <= coords_list["ivanCube"][1] <= 270):
                #print("AIAIAIAIAIAIAIAIAIAIAI")
                print(f"MOOVE MANIPULATOR TO X: {predict_list['ivanCube'][0]}; Y: {predict_list['ivanCube'][1]} in 1 second")
                move_coord = (predict_list['ivanCube'][0],200)
                bot_thread = threading.Thread(target=robot_task)
                bot_thread.start()
                bot_thread.join()
                os._exit(0)
        cv2.imshow("leoniding machin(bulochka s sosiskou)", vis)

        
        fps, fps_start_time, fps_counter = Fps(fps, fps_start_time, fps_counter)
        print(fps)
        if cv2.waitKey(1) == 27:
            break
            cv2.destroyAllWindows()
        
def check_for_stop_key():
    while True:
        if keyboard.is_pressed('shift'):
            robot.stop()
            os._exit(0)
            break
        time.sleep(0.01)

    """
    while 1:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print(f"error")
            break
        _, frame = cap.read()
        #cv2.imshow("1",frame)
        coords_to_go = wait_for_cube(frame)
        move_coord = coords_to_go
        robot_thread.start()
        
        if cv2.waitKey(1)==27:
            break
        
    """
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
cap = cv2.VideoCapture(1)


print("Video file opened successfully.")

move_robot(*robot_positions["work_pos"])
move_robot(*robot_positions["home_pos"])
grip.gripper_action(50,servo_delay = 20)
key_thread = threading.Thread(target=check_for_stop_key)
cam_thread = threading.Thread(target=control_camera)
#bot_thread = threading.Thread(target=robot_task)

cam_thread.start()
key_thread.start()
#bot_thread.start()
cam_thread.join()
key_thread.join()
#bot_thread.join()
