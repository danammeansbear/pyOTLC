from tkinter import Tk, filedialog, Canvas, Frame, Menu, Scrollbar, StringVar, Entry, Label, Button, PanedWindow
from tkinter.ttk import Treeview
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk

def detect_blobs(image):
    """Detect blobs in the image and return overlayed image and blob data."""
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 100
    params.maxArea = 1000000
    params.filterByCircularity = False

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(image)

    overlayed_img = image.copy()
    blob_data = []
    for i, keypoint in enumerate(keypoints, start=1):
        x, y = int(keypoint.pt[0]), int(keypoint.pt[1])
        size = keypoint.size
        color = image[y, x].tolist()
        hsv_color = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]
        area = np.pi * (size / 2) ** 2

        cv2.putText(
            overlayed_img,
            f"Blob {i}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
        )
        cv2.circle(overlayed_img, (x, y), int(size // 2), (0, 255, 0), 2)

        blob_data.append(
            {
                "Blob ID": f"Blob {i}",
                "Area": round(area, 2),
                "Pixel Size": round(size, 2),
                "Saturation Level": hsv_color[1],
                "Hue": hsv_color[0],
                "Value": hsv_color[2],
            }
        )
    return overlayed_img, pd.DataFrame(blob_data)

def resize_and_fit_image(canvas, img_pil, canvas_width, canvas_height):
    """Resize the image proportionally to fit within its frame."""
    img_width, img_height = img_pil.size

    scale_factor = min(canvas_width / img_width, canvas_height / img_height)
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)

    resized_img = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img_tk_resized = ImageTk.PhotoImage(resized_img)

    canvas.delete("all")
    canvas.create_image(
        canvas_width // 2,
        canvas_height // 2,
        anchor="center",
        image=img_tk_resized,
    )
    canvas.img_tk = img_tk_resized

def populate_table(tree, dataframe):
    """Populate the Treeview table with data."""
    for index, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

def filter_table(tree, dataframe, filter_var):
    """Filter the Treeview table based on the filter entry."""
    query = filter_var.get().lower()
    filtered_data = dataframe[dataframe.apply(
        lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1
    )]
    tree.delete(*tree.get_children())
    populate_table(tree, filtered_data)

def open_file(canvas, tree, filter_var, root):
    """Open an image file and process it."""
    image_path = filedialog.askopenfilename(
        title="Select Image File", filetypes=[("Image files", "*.jpg;*.png;*.jpeg")]
    )
    if not image_path:
        return

    img = cv2.imread(image_path)
    overlayed_img, blob_data = detect_blobs(img)

    img_pil = Image.fromarray(cv2.cvtColor(overlayed_img, cv2.COLOR_BGR2RGB))

    # Update canvas dynamically with image resizing
    def update_canvas(event):
        resize_and_fit_image(canvas, img_pil, event.width, event.height)

    root.bind("<Configure>", update_canvas)

    # Populate the table
    tree.delete(*tree.get_children())
    populate_table(tree, blob_data)

def main():
    root = Tk()
    root.title("Blob Detection")
    root.geometry("800x600")  # Start with a smaller default size

    # Menu
    menu_bar = Menu(root)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open File", command=lambda: open_file(canvas, tree, filter_var, root))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu_bar)

    # PanedWindow
    paned_window = PanedWindow(root, orient="horizontal")
    paned_window.pack(fill="both", expand=True)

    # Image Frame
    frame_image = Frame(paned_window, bg="gray")
    paned_window.add(frame_image, stretch="always")

    # Data Frame
    frame_data = Frame(paned_window, bg="white")
    paned_window.add(frame_data, stretch="always")

    # Image Canvas
    canvas = Canvas(frame_image, bg="black")
    canvas.pack(expand=True, fill="both")

    # Blob Data Table
    label = Label(frame_data, text="Blob Data", font=("Helvetica", 14), bg="white")
    label.pack(pady=5)

    # Filter Entry
    filter_var = StringVar()
    filter_entry = Entry(frame_data, textvariable=filter_var, font=("Helvetica", 10))
    filter_entry.pack(pady=5)

    filter_button = Button(
        frame_data,
        text="Filter",
        command=lambda: filter_table(tree, pd.DataFrame(), filter_var),
    )
    filter_button.pack(pady=5)

    # Treeview Table
    tree = Treeview(
        frame_data,
        columns=["Blob ID", "Area", "Pixel Size", "Saturation Level", "Hue", "Value"],
        show="headings",
        height=20,
    )
    for col in ["Blob ID", "Area", "Pixel Size", "Saturation Level", "Hue", "Value"]:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")
    tree.pack(expand=True, fill="both", padx=5, pady=5)

    scrollbar = Scrollbar(frame_data, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

if __name__ == "__main__":
    main()
