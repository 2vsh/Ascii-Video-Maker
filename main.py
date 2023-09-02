import tkinter as tk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
import threading
import cv2
import numpy as np
import pyautogui

# Flag to indicate stop request
stop_requested = False

def frame_to_binary(frame, threshold=127):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary

def colored_ascii_art(frame, ascii_chars, scale=10):
    h, w, _ = frame.shape
    text_frame = np.zeros((h, w, 3), dtype=np.uint8)
    num_chars = len(ascii_chars) - 1
    
    for i in range(0, h, scale):
        for j in range(0, w, scale):
            region = frame[i:i+scale, j:j+scale]
            intensity = int(np.mean(region) / 255 * num_chars)
            char = ascii_chars[intensity]
            
            color = np.mean(region, axis=(0, 1))
            cv2.putText(text_frame, char, (j, i), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
            
    return text_frame

def process_screen(ascii_chars):
    global stop_requested
    screen_width, screen_height = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('screen_output.mov', fourcc, 30.0, (screen_width, screen_height))
    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        text_frame = colored_ascii_art(frame, ascii_chars)
        cv2.imshow('Frame', text_frame)
        out.write(text_frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or stop_requested:
            break
    out.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Success", "Screen capture and processing complete.")

def process_video(video_path, ascii_chars):
    global stop_requested
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('video_output.mov', fourcc, 20.0, (width, height))
    frame_count = 0
    with ThreadPoolExecutor() as executor:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % 2 == 0:
                continue
            frame = cv2.resize(frame, (width//2, height//2))
            text_frame = colored_ascii_art(frame, ascii_chars)
            text_frame = cv2.resize(text_frame, (width, height))
            cv2.imshow('Frame', text_frame)
            out.write(text_frame)
            if cv2.waitKey(1) & 0xFF == ord('q') or stop_requested:
                break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Success", "Video processing complete.")

def start_capture(mode, video_path=None, ascii_chars="@%#*+=-:. "):
    global stop_requested
    stop_requested = False
    if mode == "screen":
        process_screen(ascii_chars)
    elif mode == "video":
        if video_path:
            process_video(video_path, ascii_chars)

def browse_file(entry):
    filepath = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filepath)

def stop_capture():
    global stop_requested
    stop_requested = True

def main():
    root = tk.Tk()
    root.title("ASCII Art Video")
    mode_var = tk.StringVar(value="screen")
    tk.Radiobutton(root, text="Screen", variable=mode_var, value="screen").pack()
    tk.Radiobutton(root, text="Video File", variable=mode_var, value="video").pack()
    tk.Label(root, text="Video File Path:").pack()
    entry = tk.Entry(root)
    entry.pack()
    tk.Button(root, text="Browse", command=lambda: browse_file(entry)).pack()
    tk.Label(root, text="ASCII Chars:").pack()
    ascii_entry = tk.Entry(root)
    ascii_entry.insert(0, "@%#*+=-:. ")
    ascii_entry.pack()
    def start():
        global stop_requested
        stop_requested = False
        mode = mode_var.get()
        video_path = entry.get() if mode == "video" else None
        ascii_chars = ascii_entry.get()
        threading.Thread(target=start_capture, args=(mode, video_path, ascii_chars)).start()
    tk.Button(root, text="Start", command=start).pack()
    tk.Button(root, text="Stop", command=stop_capture).pack()
    root.mainloop()

if __name__ == "__main__":
    main()
