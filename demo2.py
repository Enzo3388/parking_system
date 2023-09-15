import datetime
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

class Node:
    def __init__(self, plate_number, recognized_time):
        self.plate_number = plate_number
        self.recognized_time = recognized_time
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, plate_number, recognized_time):
        new_node = Node(plate_number, recognized_time)

        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node

    def print_list(self):
        current = self.head
        while current is not None:
            print(f"Plate number: {current.plate_number}, recognized time: {current.recognized_time}")
            current = current.next

class LicensePlateRecognizer:
    def __init__(self, master, width=400, height=500):
        self.master = master
        master.title("Дугаар таних систем")

        self.video_path = ""
        self.plate_number = ""

        master.configure(bg='#F0F0F0')

        self.video_label = ttk.Label(master, text="Файл сонгогдоогүй байна", font=("Helvetica", 8))
        self.video_label.pack(pady=10)

        self.select_video_button = ttk.Button(master, text="Файл сонгоно уу!", command=self.select_video)
        self.select_video_button.pack(pady=10)

        self.recognize_button = ttk.Button(master, text="Дугаар таних", command=self.recognize_plate)
        self.recognize_button.pack(pady=10)

        self.plate_label = ttk.Label(master, text="Машины дугаар: ", font=("Helvetica", 12))
        self.plate_label.pack(pady=10)

        self.thumbnail_label = ttk.Label(master)
        self.thumbnail_label.pack(pady=10)

        self.linked_list = LinkedList()

        master.geometry(f"{width}x{height}")

        button_frame = ttk.Frame(master)
        button_frame.pack()

        self.report_button = ttk.Button(button_frame, text="Тайлан", command=self.show_report)
        self.report_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.daily_report_button = ttk.Button(button_frame, text="Өдрийн тайлан", command=self.show_daily_report)
        self.daily_report_button.pack(side=tk.LEFT, padx=10, pady=10)

    def select_video(self):
        self.video_path = filedialog.askopenfilename()

        if self.video_path:
            self.video_label.configure(text=self.video_path)

            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (320, 240))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = tk.PhotoImage(data=cv2.imencode('.png', frame)[1].tobytes())
                self.thumbnail_label.configure(image=image)
                self.thumbnail_label.image = image
            cap.release()
    
    def show_report(self):
        search_window = tk.Toplevel(self.master)
        search_window.title("Search Report")

        search_label = ttk.Label(search_window, text="Автомашины дугаараар хайх:")
        search_label.pack(pady=10)

        search_entry = ttk.Entry(search_window)
        search_entry.pack(pady=10)

        remove_button = ttk.Button(search_window, text="Устгах", command=lambda: self.remove_plate(search_entry.get()))
        remove_button.pack(pady=5)

        search_button = ttk.Button(search_window, text="Хайх", command=lambda: self.search_plate(search_entry.get(), result_tree))
        search_button.pack(pady=5)

        result_tree = ttk.Treeview(search_window, columns=("Дугаар", "Орсон цаг"), show="headings")

        result_tree.column("Дугаар", width=150, anchor=tk.CENTER)
        result_tree.column("Орсон цаг", width=150, anchor=tk.CENTER)

        result_tree.heading("Дугаар", text="Дугаар")
        result_tree.heading("Орсон цаг", text="Орсон цаг")

        result_tree.pack(pady=10)

        current = self.linked_list.head
        while current is not None:
            result_tree.insert("", tk.END, values=(current.plate_number, current.recognized_time))
            current = current.next

    def search_plate(self, plate_number, result_tree):
        result_tree.delete(*result_tree.get_children())  

        if not plate_number:
            return

        current = self.linked_list.head
        while current is not None:
            if current.plate_number.lower() == plate_number.lower():
                result_tree.insert("", tk.END, values=(current.plate_number, current.recognized_time), tags=("highlight",))
            else:
                result_tree.insert("", tk.END, values=(current.plate_number, current.recognized_time))
            current = current.next

        result_tree.tag_configure("highlight", background="yellow")  

        if len(result_tree.get_children()) > 0:
            result_tree.selection_set(result_tree.get_children()[0])  
            result_tree.focus(result_tree.get_children()[0])  

    def remove_plate(self, plate_number):
        current = self.linked_list.head
        prev = None

        while current is not None:
            if current.plate_number.lower() == plate_number.lower():
                if prev is None:
                    self.linked_list.head = current.next
                else:
                    prev.next = current.next
                break

            prev = current
            current = current.next

        self.show_report()

    def show_daily_report(self):
        report_window = tk.Toplevel(self.master)
        report_window.title("Daily Report")

        report_text = tk.Text(report_window, height=10, width=50)
        report_text.pack()

        report = self.generate_daily_report()
        report_text.insert(tk.END, report)

    def generate_daily_report(self):
        
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        car_count = 0
        report = ""

        current = self.linked_list.head
        while current is not None:
            
            if current.recognized_time.startswith(current_date):
                car_count += 1
                report += f"Дугаар: {current.plate_number}, Орсон цаг: {current.recognized_time}\n"

            current = current.next

        report += f"Өнөөдөр нийт зогсоолоор үйлчлүүлсэн машины тоо: {car_count}\n"
        return report

    def recognize_plate(self):
        if not self.video_path:
            self.plate_label.config(text="Та эхлээд файлаа сонгоно уу", fg="red")
            return
        
        cap = cv2.VideoCapture(self.video_path)

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cv2.namedWindow("License Plate Recognizer", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("License Plate Recognizer", frame_width, frame_height)

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(gray, 100, 200)

            contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

                x,y,w,h = cv2.boundingRect(max_contour)
                plate_roi = gray[y:y+h, x:x+w] 

                plate_roi = cv2.GaussianBlur(plate_roi, (3, 3), 0)
                _, plate_roi = cv2.threshold(plate_roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                plate_roi = cv2.morphologyEx(plate_roi, cv2.MORPH_OPEN, kernel)

                plate_text = pytesseract.image_to_string(plate_roi, lang='mon', config='--psm 7')

                self.plate_number = plate_text.strip()

                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.linked_list.append(self.plate_number, current_time)

                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

                cv2.rectangle(frame, (0, frame_height-50), (frame_width, frame_height), (0,0,0), -1)

                cv2.putText(frame, self.plate_number, (50, frame_height-15), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            cv2.imshow("License Plate Recognizer", frame)

            cv2.waitKey(1)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            cap.release()
            cv2.destroyAllWindows()
            
            self.plate_label.configure(text="Машины дугаар: " + self.plate_number, font=("Helvetica", 15))
            
    def create_report(self):
            report_window = tk.Toplevel(self.master)
            report_window.title("Report")

            report_text = tk.Text(report_window, height=10, width=50)
            report_text.pack()

            report = ""
            current = self.linked_list.head
            while current is not None:
                report += f"Plate number: {current.plate_number}, recognized time: {current.recognized_time}\n"
                current = current.next

            report_text.insert(tk.END, report)
        
root = tk.Tk()
app = LicensePlateRecognizer(root)
root.mainloop()