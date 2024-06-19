import time

def Fps(fps, fps_start_time, fps_counter):
    fps_counter += 1
    if time.time() - fps_start_time >= 1:
        fps = fps_counter
        fps_counter = 0
        fps_start_time = time.time()
    return fps, fps_start_time, fps_counter
