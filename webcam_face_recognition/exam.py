import face_recognition
import os
import cv2
import numpy as np
import math
import datetime
import calendar
import sys
import mysql.connector



mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  #password="siva",
  database="chumma",
  port=3306,
)


mycursor = mydb.cursor()




def face_confidence(face_distance, face_match_threshold=0.7):
    range = (1- face_match_threshold)
    linear_val = (1 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'


class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()


    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f"faces/{image}")
            face_encoding = face_recognition.face_encodings(face_image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        print(self.known_face_names)

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('Video source not found...')

        while True:
            ret, frame = video_capture.read()


            if self.process_current_frame:




                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                rgb_small_frame = small_frame[:, :, ::-1]

                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:


                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    confidence = '???'



                    # Calculate the shortest distance to face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])


                    self.face_names.append(f'{name} ({confidence})')



                    # Get the current date and time
                    now = datetime.datetime.now()


                    # Print the employee name and entering time
                    print(f"{name} entered on {now.strftime('%Y-%m-%d')} at {now.strftime('%H:%M:%S')}")
                    #print(f"{name} entered at {now.strftime('%Y-%m-%d %H:%M:%S')}")



                    # Store the employee name and entering time in the MySQL database
                    sql = "INSERT INTO employee_time(name, in_time) VALUES (%s, %s)"
                    val = (name, now)
                    mycursor.execute(sql, val)
                    mydb.commit()

            self.process_current_frame = not self.process_current_frame



            #rusults display
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations
                top *= 4
                right *= 4  
                bottom *= 4
                left *= 4



                # Create the frame with the name
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 5)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)




            # Display the resulting image
            cv2.imshow('Face Recognition', frame)




               # to quit the result windowz
            if cv2.waitKey(1) == ord('q'):
                break




        # destroy frame window
        video_capture.release()
        cv2.destroyAllWindows()







if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()
