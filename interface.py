import cv2
import pandas as pd
from ultralytics import YOLO
import numpy as np
import easyocr
from datetime import datetime
import tkinter as tk
from tkinter import Frame
from PIL import Image, ImageTk
import threading
import psycopg2

# Inicializa o leitor EasyOCR
reader = easyocr.Reader(['en'])

# Carrega o modelo YOLOv8 pré-treinado
model = YOLO('/home/jose/ocrb/modelo/best.pt')

# Lista de classes para YOLO
with open("/home/jose/ocrb/coco1.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

# Área de análise original
original_width, original_height = 1020, 510
analysis_ratio = 0.30

# Conectar ao banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname="controle", user="postgres", password="1234", host="localhost"
)
cursor = conn.cursor()

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entrada (
        placa VARCHAR(20),
        data DATE,
        hora TIME,
        img BYTEA
    );
    CREATE TABLE IF NOT EXISTS saida (
        placa VARCHAR(20),
        data DATE,
        hora TIME,
        img BYTEA
    );
    CREATE TABLE IF NOT EXISTS registro_placas (
        placa VARCHAR(20) PRIMARY KEY,
        ultimo_registro TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS historico_entrada (
        placa VARCHAR(20),
        data DATE,
        hora TIME,
        img BYTEA
    );
    """)
    conn.commit()

def insert_entrada(placa, data, hora, img):
    cursor.execute("""
    INSERT INTO entrada (placa, data, hora, img)
    VALUES (%s, %s, %s, %s);
    """, (placa, data, hora, psycopg2.Binary(img)))
    
    # Adiciona o mesmo registro à tabela historico_entrada
    cursor.execute("""
    INSERT INTO historico_entrada (placa, data, hora, img)
    VALUES (%s, %s, %s, %s);
    """, (placa, data, hora, psycopg2.Binary(img)))
    
    conn.commit()

def insert_saida(placa, data, hora, img):
    cursor.execute("""
    INSERT INTO saida (placa, data, hora, img)
    VALUES (%s, %s, %s, %s);
    """, (placa, data, hora, psycopg2.Binary(img)))
    conn.commit()

def delete_entrada(placa):
    cursor.execute("""
    SELECT * FROM entrada WHERE placa = %s;
    """, (placa,))
    record = cursor.fetchone()
    if record:
        # Move o registro para a tabela de saída
        cursor.execute("""
        INSERT INTO saida (placa, data, hora, img)
        VALUES (%s, %s, %s, %s);
        """, (record[0], record[1], record[2], record[3]))
        
        # Remove o registro da tabela de entrada
        cursor.execute("""
        DELETE FROM entrada
        WHERE placa = %s;
        """, (placa,))
        conn.commit()

def delete_saida(placa):
    cursor.execute("""
    DELETE FROM saida
    WHERE placa = %s;
    """, (placa,))
    conn.commit()

def update_plate_registration(placa):
    now = datetime.now()
    cursor.execute("""
        INSERT INTO registro_placas (placa, ultimo_registro)
        VALUES (%s, %s)
        ON CONFLICT (placa) 
        DO UPDATE SET ultimo_registro = EXCLUDED.ultimo_registro
    """, (placa, now))
    conn.commit()

def resize_analysis_area(original_width, original_height, target_width, target_height):
    x_min_area, y_min_area, x_max_area, y_max_area = 30, 390, 1015, 451
    width_scale = target_width / original_width
    height_scale = target_height / original_height
    x_min_area = int(x_min_area * width_scale)
    y_min_area = int(y_min_area * height_scale)
    x_max_area = int(x_max_area * width_scale)
    y_max_area = int(y_max_area * height_scale)
    x_min_area = max(0, x_min_area)
    y_min_area = max(0, y_min_area)
    x_max_area = min(target_width, x_max_area)
    y_max_area = min(target_height, y_max_area)
    return x_min_area, y_min_area, x_max_area, y_max_area

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoramento de Câmeras")
        self.root.geometry("1200x800")
        
        self.rtsp_links = [
            '/home/jose/ocrb/resources/mycarplate.mp4',
        ]
        
        self.frames = [None] * len(self.rtsp_links)
        self.canvas = [None] * len(self.rtsp_links)
        self.video_sources = [None] * len(self.rtsp_links)
        
        self.frame_counters = [0] * len(self.rtsp_links)  # Contador de frames
        self.frame_buffer = [None] * len(self.rtsp_links)  # Buffer para frames
        
        self.create_widgets()
        self.start_video_stream()

    def create_widgets(self):
        for i in range(len(self.rtsp_links)):
            frame = Frame(self.root, width=600, height=360)
            frame.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.canvas[i] = tk.Canvas(frame, width=600, height=360)
            self.canvas[i].pack()

    def analyze_frame(self, frame):
        height, width = frame.shape[:2]
        x_min_area, y_min_area, x_max_area, y_max_area = resize_analysis_area(original_width, original_height, width, height)
        
        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        current_time = datetime.now()
        for index, row in px.iterrows():
            x1, y1, x2, y2, _, d = map(int, row)
            c = class_list[d]
            cx = int(x1 + x2) // 2
            cy = int(y1 + y2) // 2
            if x_min_area <= cx <= x_max_area and y_min_area <= cy <= y_max_area:
                crop = frame[y1:y2, x1:x2]
                _, img_encoded = cv2.imencode('.jpg', crop)
                img_bytes = img_encoded.tobytes()
                
                text = reader.readtext(crop, detail=0, paragraph=False)
                if text:
                    text = text[0].replace('(', '').replace(')', '').replace(',', '').replace(']', '')
                    if text:
                        cursor.execute("SELECT ultimo_registro FROM registro_placas WHERE placa = %s", (text,))
                        result = cursor.fetchone()
                        if result:
                            ultimo_registro = result[0]
                            if (current_time - ultimo_registro).total_seconds() < 5:
                                continue
                        update_plate_registration(text)
                        cursor.execute("SELECT * FROM entrada WHERE placa = %s", (text,))
                        entry_exists = cursor.fetchone()
                        if entry_exists:
                            delete_entrada(text)
                            insert_saida(text, current_time.date(), current_time.time(), img_bytes)
                        else:
                            cursor.execute("SELECT * FROM saida WHERE placa = %s", (text,))
                            exit_exists = cursor.fetchone()
                            if exit_exists:
                                delete_saida(text)
                                insert_entrada(text, current_time.date(), current_time.time(), img_bytes)
                            else:
                                insert_entrada(text, current_time.date(), current_time.time(), img_bytes)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                        cv2.imshow('crop', crop)
        
        cv2.rectangle(frame, (x_min_area, y_min_area), (x_max_area, y_max_area), (255, 0, 0), 2)
        return frame

    def update_frame(self, index):
        while True:
            ret, frame = self.video_sources[index].read()
            if not ret:
                break
            
            # Armazenar o frame no buffer
            self.frame_buffer[index] = frame
            
            # Desenhar a área de análise no frame original
            height, width = frame.shape[:2]
            x_min_area, y_min_area, x_max_area, y_max_area = resize_analysis_area(original_width, original_height, width, height)
            cv2.rectangle(frame, (x_min_area, y_min_area), (x_max_area, y_max_area), (255, 0, 0), 2)
            
            # Incrementar o contador de frames
            self.frame_counters[index] += 1
            
            # Processar o frame apenas se o contador for um múltiplo de 4
            if self.frame_counters[index] % 4 == 0:
                # Pegar o último frame do buffer para análise
                frame_to_analyze = self.frame_buffer[index]
                if frame_to_analyze is not None:
                    frame_to_analyze = self.analyze_frame(frame_to_analyze)
            
            # Redimensionar e exibir o frame
            height, width = frame.shape[:2]
            aspect_ratio = width / height
            new_height = 360
            new_width = int(new_height * aspect_ratio)
            if new_width > 600:
                new_width = 600
                new_height = int(new_width / aspect_ratio)
            resized_frame = cv2.resize(frame, (new_width, new_height))
            padding_frame = np.zeros((360, 600, 3), dtype=np.uint8)
            padding_frame[:new_height, :new_width] = resized_frame
            frame = cv2.cvtColor(padding_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            
            def update_canvas():
                self.canvas[index].create_image(0, 0, image=photo, anchor=tk.NW)
                self.canvas[index].image = photo
            
            self.root.after(0, update_canvas)
            cv2.waitKey(1)

    def start_video_stream(self):
        for i in range(len(self.rtsp_links)):
            self.video_sources[i] = cv2.VideoCapture(self.rtsp_links[i])
            thread = threading.Thread(target=self.update_frame, args=(i,))
            thread.daemon = True
            thread.start()

    def open_report(self):
        import relatorio  # Importe seu módulo de relatório
        relatorio.open_report_window()  # Supondo que a função exista

def close_db_connection():
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()  # Certifique-se de criar as tabelas antes de iniciar
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
    close_db_connection()  # Fechar a conexão ao terminar
