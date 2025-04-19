import cv2
from ultralytics import YOLO

model = YOLO("yolo.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, device="cpu", verbose=False)
    num_people = len(results[0].boxes)
    print(num_people)
    annotated_frame = results[0].plot()

    cv2.imshow("YOLO Real Time Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
