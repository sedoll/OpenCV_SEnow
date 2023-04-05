import tkinter as tk
import tkinter.ttk as ttk
import cv2
import PIL.Image, PIL.ImageTk

class WebcamApp:
    def __init__(self, window, video_source=0):
        self.window = window
        self.window.title("Animal_Camera")

        # Open the video source
        self.cap = cv2.VideoCapture(video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        # Create a button to take snapshots
        self.snapshot_button = ttk.Button(window, text="Snapshot", command=self.snapshot)
        self.snapshot_button.pack(fill=tk.BOTH, expand=True)

        self.window.bind('p', self.snapshot)
        
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.cap.read()

        if ret:
            # Convert the frame from BGR to RGB color space
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to ImageTk format
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2image))

            # Update the canvas with the new photo
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # Call the update method again after delay milliseconds
        self.window.after(self.delay, self.update)
        

    def snapshot(self, event=None):
        # Get a frame from the video source
        ret, frame = self.cap.read()

        if ret:
            # Save the snapshot as a png file
            print('이미지 저장')
            cv2.imwrite("snapshot.png", frame)

if __name__ == '__main__':
    # Create a window and pass it to the WebcamApp class
    WebcamApp(tk.Tk())