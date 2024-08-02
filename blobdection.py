import cv2
from skimage.feature import blob_log
from tkinter import Tk, Button, Label, filedialog, Frame, PhotoImage
import numpy as np
from PIL import Image, ImageTk
import threading
import queue

class BlobThread(threading.Thread):
    def __init__(self, image_path, queue):
        threading.Thread.__init__(self)
        self.image_path = image_path
        self.queue = queue

    def run(self):
        image = cv2.imread(self.image_path, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (500, 500))  # Resize the image to 500x500
        image_with_blobs, blobs = self.segment_image(image)
        image_tk = self.convert_to_tk(image_with_blobs)
        self.queue.put((image_tk, blobs))

    def segment_image(self, image):
        blobs = blob_log(image, min_sigma=0.1, max_sigma=30, threshold=0.02)
        image_with_blobs = image.copy()
        for y, x, r in blobs:
            r_int = int(round(r))
            cv2.circle(image_with_blobs, (int(x), int(y)), r_int, (0, 0, 255), -1)
        return image_with_blobs, blobs

    def convert_to_tk(self, image):
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_pil = image_pil.resize((500, 500), Image.ANTIALIAS)  # Resize to 500x500
        image_tk = ImageTk.PhotoImage(image=image_pil)
        return image_tk

def select_image():
    """Opens a file explorer window and allows the user to select an image."""
    filename = filedialog.askopenfilename(title="Select image")
    return filename

def display_selected_image(image_path, blobs_queue, image_label):
    """Reads the selected image, starts a new blob thread, and displays it with blobs."""
    if image_path:
        blob_thread = BlobThread(image_path, blobs_queue)
        blob_thread.start()
        update_display(image_label, blobs_queue)

def update_display(image_label, blobs_queue):
    """Updates the displayed image with blobs."""
    try:
        image_tk, blobs = blobs_queue.get_nowait()
        display_image(image_tk, image_label)
        # Inform the user if no blobs were found
        if not blobs:
            print("No blobs found in the image.")
        # Update label with relevant information if blobs were found
        else:
            print(f"Detected {len(blobs)} blobs. Click on the image to see individual information.")
    except queue.Empty:
        # If the queue is empty, schedule the function to be called again after a delay
        image_label.after(100, lambda: update_display(image_label, blobs_queue))

def display_image(image_tk, image_label):
    """Displays the image and updates the image label on the screen."""
    image_label.config(image=image_tk)
    image_label.image = image_tk

def display_blob_info(event, blobs):
    """Displays the blob information based on the click location and blob data."""
    x, y = event.x, event.y
    # Calculate blob index based on click coordinates and blob size
    blob_index = (y // 10) * image.shape[1] + (x // 10)
    # Check if index is within bounds
    if 0 <= blob_index < len(blobs):
        blob_info = get_blob_info(blobs[blob_index])
        print(f"Blob Information: {blob_info}")

def get_blob_info(blob):
    """Returns a dictionary containing the properties of a blob."""
    y, x, r = blob
    return {
        "Area": np.pi * r**2,
        "Perimeter": 2 * np.pi * r,
        "Center": (x, y),
    }

def main():
    # Create the main window
    root = Tk()
    root.title("Blob Detection")

    # Initialize blob queue
    blobs_queue = queue.Queue()

    # Create a frame for the image and buttons
    image_frame = Frame(root)
    image_frame.pack(padx=10, pady=10)

    # Create a button to select an image
    select_image_button = Button(image_frame, text="Select Image",
                                 command=lambda: display_selected_image(select_image(), blobs_queue, image_label))
    select_image_button.pack()

    # Create a label to display the image
    image_label = Label(image_frame)
    image_label.pack()

    # Create a frame for the blob information
    info_frame = Frame(root)
    info_frame.pack(padx=10, pady=10)

    # Create a label to display the blob information
    info_label = Label(info_frame, text="Blob Information")
    info_label.pack()

    # Bind the mouse click event to the image label
    image_label.bind("<Button-1>", lambda event: display_blob_info(event, blobs_queue.get()[1]))

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
