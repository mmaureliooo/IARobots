import cv2
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class DatasetCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Captura de muestras para IA")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Índice de cámara: prueba 0 o 1 según tu equipo
        self.camera_index = 1
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir la cámara.")
            self.root.destroy()
            return

        # Carpeta base del dataset
        self.base_dir = Path("dataset")
        self.labels = ["circulo", "cuadrado", "triangulo"]

        self.create_directories()

        # Frame actual capturado desde cámara
        self.current_frame = None

        # Interfaz
        self.video_label = tk.Label(self.root)
        self.video_label.pack(padx=10, pady=10)

        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        self.btn_circulo = tk.Button(
            buttons_frame,
            text="Foto círculo",
            width=18,
            command=lambda: self.save_photo("circulo")
        )
        self.btn_circulo.grid(row=0, column=0, padx=5, pady=5)

        self.btn_cuadrado = tk.Button(
            buttons_frame,
            text="Foto cuadrado",
            width=18,
            command=lambda: self.save_photo("cuadrado")
        )
        self.btn_cuadrado.grid(row=0, column=1, padx=5, pady=5)

        self.btn_triangulo = tk.Button(
            buttons_frame,
            text="Foto triángulo",
            width=18,
            command=lambda: self.save_photo("triangulo")
        )
        self.btn_triangulo.grid(row=0, column=2, padx=5, pady=5)

        self.info_label = tk.Label(self.root, text="Muestra el objeto frente a la cámara y pulsa el botón correspondiente.")
        self.info_label.pack(pady=5)

        self.counter_label = tk.Label(self.root, text=self.build_counter_text(), justify="left")
        self.counter_label.pack(pady=5)

        self.update_video()

    def create_directories(self):
        self.base_dir.mkdir(exist_ok=True)
        for label in self.labels:
            (self.base_dir / label).mkdir(exist_ok=True)

    def get_next_filename(self, label: str) -> Path:
        folder = self.base_dir / label
        existing_files = list(folder.glob(f"{label}_*.jpg"))

        max_id = 0
        for file_path in existing_files:
            stem = file_path.stem  # ejemplo: circulo_0007
            parts = stem.split("_")
            if len(parts) >= 2 and parts[-1].isdigit():
                max_id = max(max_id, int(parts[-1]))

        next_id = max_id + 1
        filename = f"{label}_{next_id:04d}.jpg"
        return folder / filename

    def build_counter_text(self) -> str:
        lines = ["Número de imágenes guardadas:"]
        for label in self.labels:
            count = len(list((self.base_dir / label).glob("*.jpg")))
            lines.append(f"  {label}: {count}")
        return "\n".join(lines)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()

            # Convertir BGR -> RGB para mostrar en Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Opcional: redimensionar para que quepa mejor en ventana
            frame_rgb = cv2.resize(frame_rgb, (800, 600))

            image = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=image)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(20, self.update_video)

    def save_photo(self, label: str):
        if self.current_frame is None:
            messagebox.showwarning("Aviso", "Todavía no hay imagen disponible de la cámara.")
            return

        save_path = self.get_next_filename(label)

        # Guardamos el frame original, no el redimensionado de pantalla
        success = cv2.imwrite(str(save_path), self.current_frame)

        if success:
            self.info_label.config(text=f"Guardada: {save_path}")
            self.counter_label.config(text=self.build_counter_text())
        else:
            messagebox.showerror("Error", "No se pudo guardar la imagen.")

    def on_close(self):
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetCaptureApp(root)
    root.mainloop()