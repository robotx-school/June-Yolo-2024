from ultralytics import YOLO
import cv2
import numpy as np
from collections import defaultdict
from predict_position import predict_position

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

model = YOLO("best2.pt")
counter_moving = {"blue":0,"red":0,"purple":0}
move_coord = []
track_history = defaultdict(lambda: [])
def check_cube(frame,fps):
    results = model.track(frame, persist=True)
    coords_list = {"ShebaCube":[],"ivanCube":[],"SUSCube":[]}
    predict_list = {"ShebaCube":[],"ivanCube":[],"SUSCube":[]}

    if results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu()
        boxes_xyxy = results[0].boxes.xyxy.cpu()

        classes_names = results[0].names
        classes = results[0].boxes.cls.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        frame = results[0].plot()#annot
        
        for box, track_id, box_xyxy, class_id in zip(boxes, track_ids, boxes_xyxy, classes):

            class_name = classes_names[int(class_id)]
            x, y, w, h = box
            x1, y1, x2, y2 = box_xyxy
            track = track_history[track_id]

            if len(track)>=2:
                print("track [-1]", track[-1])
            track.append((float(x), float(y)))
            
            if len(track)>=2 and class_name == "ShebaCube":
                if abs(track[-1][0] - track[-2][0])<=2 and abs(track[-1][1] - track[-2][1])<=1:
                    counter_moving["blue"] += 1
                else:
                    counter_moving["blue"] = 0

            if len(track)>=2 and class_name == "SUSCube":
                if abs(track[-1][0] - track[-2][0])<=2 and abs(track[-1][1] - track[-2][1])<=1:
                    counter_moving["purple"] += 1
                else:
                    counter_moving["purple"] = 0

            if len(track)>=2 and class_name == "ivanCube":
                if abs(track[-1][0] - track[-2][0])<=2 and abs(track[-1][1] - track[-2][1])<=1:
                    counter_moving["red"] += 1
                else:
                    counter_moving["red"] = 0

            #print(counter_moving["red"])
            if len(track) > 3:
                track.pop(0)
            
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            x_mm, y_mm = (points[0][0][0]*515)/640+150,(points[0][0][1]*315)/480+50
            coords_list[class_name] = (x_mm,y_mm)
            #315x515
            cv2.polylines(frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            x_pred, y_pred = predict_position(track,3,fps)

            x_pred_mm, y_pred_mm = (x_pred*515)/640+150,(y_pred*315)/480+50

            predict_list[class_name] = (x_pred_mm,y_pred_mm)
            cv2.circle(frame, (int(x_pred), int(y_pred)), 5, (0, 255, 0), -1)
            cv2.putText(frame, 'Predicted', (int(x_pred), int(y_pred)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            #print("predict liat added")
        return predict_list, track, coords_list, counter_moving,frame
            #cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    else:
        return predict_list,counter_moving,coords_list,None,frame
