import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

try:
    import pytesseract
except ImportError:
    print("Pytesseract not found. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "pytesseract"])
    import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class LicensePlateRecognizer:
    def __init__(self, master, width=400, height=500):
        self.master = master
        master.title("Дугаар таних систем")

        self.image_path = ""
        self.plate_number = ""

        master.configure(bg='#F0F0F0')

        self.image_label = ttk.Label(master, text="Файл сонгогдоогүй байна", font=("Helvetica", 8))
        self.image_label.pack(pady=10)

        self.select_image_button = ttk.Button(master, text="Файл сонгоно уу!", command=self.select_image)
        self.select_image_button.pack(pady=10)

        self.recognize_button = ttk.Button(master, text="Дугаар таних", command=self.recognize_plate)
        self.recognize_button.pack(pady=10)

        self.plate_label = ttk.Label(master, text="Машины дугаар: ", font=("Helvetica", 12))
        self.plate_label.pack(pady=10)

        self.thumbnail_label = ttk.Label(master)
        self.thumbnail_label.pack(pady=10)

        master.geometry(f"{width}x{height}")

    def select_image(self):
        self.image_path = filedialog.askopenfilename()

        if self.image_path:
            self.image_label.configure(text=self.image_path)

            frame = cv2.imread(self.image_path)
            if frame is not None:
                frame = cv2.resize(frame, (320, 240))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = tk.PhotoImage(data=cv2.imencode('.png', frame)[1].tobytes())
                self.thumbnail_label.configure(image=image)
                self.thumbnail_label.image = image
    
    def recognize_plate(self):
        if not self.image_path:
            self.plate_label.config(text="Та эхлээд файлаа сонгоно уу", fg="red")
            return

        frame = cv2.imread(self.image_path)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Canny edge detection to the grayscale image
        edges = cv2.Canny(gray, 100, 200)

        # Find contours in the edge image
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the contour with the largest area that meets certain criteria (aspect ratio, area)
        max_contour = None
        max_area = 0
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            area = cv2.contourArea(contour)
            if aspect_ratio > 2 and aspect_ratio < 6 and area > 1000 and area > max_area:
                max_contour = contour
                max_area = area

        if max_contour is not None:

            # Define the ROI around
            x,y,w,h = cv2.boundingRect(max_contour)
            plate_roi = gray[y:y+h, x:x+w] 

                # Preprocess the image
            plate_roi = cv2.GaussianBlur(plate_roi, (3, 3), 0)
            _, plate_roi = cv2.threshold(plate_roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

                # Remove noise from the image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            plate_roi = cv2.morphologyEx(plate_roi, cv2.MORPH_OPEN, kernel)

                # Perform OCR on the plate ROI using Tesseract
            plate_text = pytesseract.image_to_string(plate_roi, lang='mon', config='--psm 7')

                # Store the recognized license plate number in self.plate_number
            self.plate_number = plate_text.strip()

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.linked_list.append(self.plate_number, current_time)

                # Draw a rectangle around the contour on the original frame
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

                # Draw a black rectangle at the bottom of the frame to display the license plate number
            cv2.rectangle(frame, (0, frame_height-50), (frame_width, frame_height), (0,0,0), -1)

                # Draw the license plate number on the black rectangle
            cv2.putText(frame, self.plate_number, (50, frame_height-15), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            # Display the frame in the window
            cv2.imshow("License Plate Recognizer", frame)

            # Wait for 1 millisecond before displaying the next frame
            cv2.waitKey(1)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            cap.release()
            cv2.destroyAllWindows()
            

            self.plate_label.configure(text="Машины дугаар: " + self.plate_number, font=("Helvetica", 15))
root = tk.Tk()
app = LicensePlateRecognizer(root)
root.mainloop()