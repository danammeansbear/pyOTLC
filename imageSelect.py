import cv2
import numpy as np
from tkinter import Tk, filedialog, Canvas, Frame, Label, Text, Scrollbar
import pandas as pd
from PIL import Image, ImageTk

def get_image_path():
    root = Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(
        title="Select Image File", filetypes=[("Image files", "*.jpg;*.png;*.jpeg")]
    )

    root.destroy()  # Close the Tkinter window

    return file_path

# Load the image without converting to grayscale
image_path = get_image_path()
img = cv2.imread(image_path)

# Set up the blob detector with modified parameters
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 500  # Filter blobs smaller than 100 pixels
params.maxArea = 1000000  # Filter blobs larger than 10000 pixels
params.filterByCircularity = True
params.minCircularity = 0.7  # Filter elongated blobs
detector = cv2.SimpleBlobDetector_create(params)

# Detect blobs
keypoints = detector.detect(img)

# Create a DataFrame to store blob information
blob_data = pd.DataFrame(columns=["Area", "Saturation", "Hue", "Value",
                                  "Normalized_X", "Normalized_Y",
                                  "Aspect_Ratio", "Orientation", "Eccentricity",
                                  "Color_BGR", "Color_Lab"])

# Draw detected blobs with labels
img_with_labels = img.copy()
for idx, keypoint in enumerate(keypoints):
    x_center, y_center = int(keypoint.pt[0]), int(keypoint.pt[1])

    # Draw label above the blob
    label = f"Blob {idx+1}"
    cv2.putText(img_with_labels, label, (x_center, y_center-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Store blob information in the DataFrame
    area = keypoint.size
    hsv_color = cv2.cvtColor(np.uint8([[img[y_center, x_center]]]), cv2.COLOR_BGR2HSV)[0][0]
    saturation, hue, value = hsv_color[1], hsv_color[0], hsv_color[2]
    normalized_x, normalized_y = x_center / img.shape[1], y_center / img.shape[0]
    aspect_ratio, orientation, eccentricity = area / area, keypoint.angle, area / np.sqrt(area)
    color_bgr, color_lab = img[y_center, x_center], cv2.cvtColor(np.uint8([[img[y_center, x_center]]]), cv2.COLOR_BGR2Lab)[0][0]

    blob_data = blob_data.append({
        "Area": area,
        "Saturation": saturation,
        "Hue": hue,
        "Value": value,
        "Normalized_X": normalized_x,
        "Normalized_Y": normalized_y,
        "Aspect_Ratio": aspect_ratio,
        "Orientation": orientation,
        "Eccentricity": eccentricity,
        "Color_BGR": color_bgr,
        "Color_Lab": color_lab
    }, ignore_index=True)

# Create a Tkinter window to display the image and blob information
root = Tk()
root.title("Blob Information")

# Set maximum size for the window
max_width = 1200  # 500 for image, 500 for data table, and additional space for padding
max_height = 600  # Adjust as needed
root.geometry(f"{max_width}x{max_height}")

# Convert OpenCV image to Pillow format
img_pil = Image.fromarray(cv2.cvtColor(img_with_labels, cv2.COLOR_BGR2RGB))
img_tk = ImageTk.PhotoImage(img_pil)

# Display the image and blob information in separate frames
frame_image = Frame(root, width=500, height=500)
frame_image.pack(side="left", padx=10, pady=10)

# Image canvas
canvas = Canvas(frame_image, width=img.shape[1], height=img.shape[0])
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, anchor="nw", image=img_tk)

# Create a frame to hold blob information
frame_data = Frame(root, width=500, height=500)
frame_data.pack(side="right", padx=10, pady=10)

# Blob information text box with scrollbar
text_box = Text(frame_data, wrap="word", height=20, width=40)
scrollbar = Scrollbar(frame_data, command=text_box.yview)
text_box.config(yscrollcommand=scrollbar.set)
text_box.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Insert blob_data into the text box
text_box.insert("1.0", str(blob_data))

root.mainloop()