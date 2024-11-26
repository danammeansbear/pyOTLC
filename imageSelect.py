from tkinter import Tk, filedialog, Canvas, Frame, Menu, Scrollbar, StringVar, Entry, Label, Button, PanedWindow, Toplevel
from tkinter.ttk import Treeview
from PIL import Image, ImageTk, ImageSequence
import cv2
import numpy as np
import pandas as pd


def show_modal_loading_screen(root, gif_path="loading.gif"):
    """Show a modal loading screen with a GIF."""
    loading_screen = Toplevel(root)
    loading_screen.title("Loading...")
    loading_screen.geometry("400x300")
    loading_screen.resizable(False, False)

    # Center the loading screen over the main window
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 200
    y = root.winfo_y() + (root.winfo_height() // 2) - 150
    loading_screen.geometry(f"+{x}+{y}")

    # Prevent interaction with the main window
    loading_screen.transient(root)
    loading_screen.grab_set()

    # Add GIF as the loading animation
    gif_label = Label(loading_screen)
    gif_label.pack(expand=True, fill="both")

    # Load and play the GIF
    frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(Image.open(gif_path))]

    def update_frame(frame_index=0):
        frame = frames[frame_index]
        gif_label.configure(image=frame)
        next_frame = (frame_index + 1) % len(frames)
        loading_screen.after(100, update_frame, next_frame)

    update_frame()
    return loading_screen


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


def open_file(label, canvas, tree, filter_var, root, gif_path="loading.gif"):
    """Open an image file, process it, and display the results."""
    image_path = filedialog.askopenfilename(
        title=f"Select {label} Image File", filetypes=[("Image files", "*.jpg;*.png;*.jpeg")]
    )
    if not image_path:
        return

    # Show the loading screen
    loading_screen = show_modal_loading_screen(root, gif_path)

    # Process the image after showing the loading screen
    root.after(100, lambda: process_image(label, image_path, canvas, tree, filter_var, root, loading_screen))


def process_image(label, image_path, canvas, tree, filter_var, root, loading_screen):
    """Process the selected image."""
    img = cv2.imread(image_path)
    overlayed_img, blob_data = detect_blobs(img)

    img_pil = Image.fromarray(cv2.cvtColor(overlayed_img, cv2.COLOR_BGR2RGB))

    # Update canvas dynamically with image resizing
    def update_canvas(event):
        resize_and_fit_image(canvas, img_pil, event.width, event.height)

    root.bind("<Configure>", update_canvas)

    # Update the canvas and table based on the label
    canvas.delete("all")
    resize_and_fit_image(canvas, img_pil, canvas.winfo_width(), canvas.winfo_height())
    tree.delete(*tree.get_children())
    populate_table(tree, blob_data)

    # Close the loading screen
    loading_screen.destroy()


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


def main():
    root = Tk()
    root.title("Blob Detection - Control and Test")
    root.geometry("1200x800")

    # PanedWindow
    paned_window = PanedWindow(root, orient="vertical")
    paned_window.pack(fill="both", expand=True)

    # Control Section
    frame_control = Frame(paned_window, bg="lightgray", pady=10)
    paned_window.add(frame_control, stretch="always")
    Label(frame_control, text="Control Image and Data Table", font=("Helvetica", 16), bg="lightgray").pack()

    canvas_control = Canvas(frame_control, bg="black", height=300)
    canvas_control.pack(expand=True, fill="both", pady=5)

    tree_control = Treeview(
        frame_control,
        columns=["Blob ID", "Area", "Pixel Size", "Saturation Level", "Hue", "Value"],
        show="headings",
        height=10,
    )
    for col in ["Blob ID", "Area", "Pixel Size", "Saturation Level", "Hue", "Value"]:
        tree_control.heading(col, text=col)
        tree_control.column(col, width=150, anchor="center")
    tree_control.pack(expand=True, fill="both", padx=5, pady=5)

    Button(
        frame_control,
        text="Select Control Image",
        command=lambda: open_file("Control", canvas_control, tree_control, None, root),
    ).pack(pady=10)

    # Test Section
    frame_test = Frame(paned_window, bg="lightblue", pady=10)
    paned_window.add(frame_test, stretch="always")
    Label(frame_test, text="Test Image and Data Table", font=("Helvetica", 16), bg="lightblue").pack()

    canvas_test = Canvas(frame_test, bg="black", height=300)
    canvas_test.pack(expand=True, fill="both", pady=5)

    tree_test = Treeview(
        frame_test,
        columns=["Blob ID", "Area", "Pixel Size", "Saturation Level", "Hue", "Value"],
        show="headings",
        height=10,
    )
    for col in ["Blob ID", "Area", "Pixel Size", "Saturation Level", "Hue", "Value"]:
        tree_test.heading(col, text=col)
        tree_test.column(col, width=150, anchor="center")
    tree_test.pack(expand=True, fill="both", padx=5, pady=5)

    Button(
        frame_test,
        text="Select Test Image",
        command=lambda: open_file("Test", canvas_test, tree_test, None, root),
    ).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
