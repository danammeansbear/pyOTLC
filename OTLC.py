import cv2
import numpy as np
from tkinter import Tk, filedialog, Canvas, Frame, Scrollbar, Button, Label, Scale
from tkinter import ttk, IntVar, StringVar, DoubleVar, HORIZONTAL
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os
import csv

class TLCAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("TLC Analyzer")
        
        # Get screen dimensions and set window size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        initial_width = int(screen_width * 0.9)
        initial_height = int(screen_height * 0.9)
        self.root.geometry(f"{initial_width}x{initial_height}")
        
        # Make the window responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Variables
        self.image_path = None
        self.img = None
        self.img_with_labels = None
        self.pil_image = None
        self.photo_image = None
        self.keypoints = None
        self.blob_data = None
        self.lanes = []
        
        # Detection parameters - TLC optimized with default values
        self.min_area = IntVar(value=100)
        self.max_area = IntVar(value=10000)
        self.min_circularity = DoubleVar(value=0.5)
        self.threshold_min = IntVar(value=50)
        self.threshold_max = IntVar(value=255)
        self.invert_image = IntVar(value=0)
        self.num_lanes = IntVar(value=1)
        self.lane_width = IntVar(value=50)
        
        # Create main layout
        self.create_layout()
        
        # Start with file dialog
        self.load_image()
    
    def create_layout(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create tabs
        self.main_tab = Frame(self.notebook)
        self.analysis_tab = Frame(self.notebook)
        self.calibration_tab = Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="TLC Image")
        self.notebook.add(self.analysis_tab, text="Analysis")
        self.notebook.add(self.calibration_tab, text="Calibration")
        
        # Configure tabs to expand
        for tab in [self.main_tab, self.analysis_tab, self.calibration_tab]:
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
        
        # === Main Tab ===
        main_paned = ttk.PanedWindow(self.main_tab, orient="horizontal")
        main_paned.grid(row=0, column=0, sticky="nsew")
        
        # Left frame for image and controls
        self.left_frame = Frame(main_paned)
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=1)
        
        # Right frame for spot data
        self.right_frame = Frame(main_paned)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)
        
        main_paned.add(self.left_frame, weight=3)
        main_paned.add(self.right_frame, weight=2)
        
        # Image frame with controls below
        image_controls_frame = Frame(self.left_frame)
        image_controls_frame.grid(row=0, column=0, sticky="nsew")
        image_controls_frame.columnconfigure(0, weight=1)
        image_controls_frame.rowconfigure(0, weight=1)
        
        # Canvas for image
        self.canvas_frame = Frame(image_controls_frame)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = Canvas(self.canvas_frame, bg="lightgray")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars for canvas
        self.h_scrollbar = Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.v_scrollbar = Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Control panel
        control_frame = ttk.LabelFrame(image_controls_frame, text="Detection Controls")
        control_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Controls - first row
        ttk.Label(control_frame, text="Min Area:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        min_area_scale = ttk.Scale(control_frame, from_=10, to=1000, variable=self.min_area, orient="horizontal")
        min_area_scale.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        min_area_scale.bind("<ButtonRelease-1>", lambda e: self.detect_spots())
        ttk.Label(control_frame, textvariable=self.min_area).grid(row=0, column=2, padx=5, pady=2, sticky="w")
        
        ttk.Label(control_frame, text="Max Area:").grid(row=0, column=3, padx=5, pady=2, sticky="w")
        max_area_scale = ttk.Scale(control_frame, from_=1000, to=50000, variable=self.max_area, orient="horizontal")
        max_area_scale.grid(row=0, column=4, padx=5, pady=2, sticky="ew")
        max_area_scale.bind("<ButtonRelease-1>", lambda e: self.detect_spots())
        ttk.Label(control_frame, textvariable=self.max_area).grid(row=0, column=5, padx=5, pady=2, sticky="w")
        
        # Controls - second row
        ttk.Label(control_frame, text="Min Circularity:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        circ_scale = ttk.Scale(control_frame, from_=0.1, to=1.0, variable=self.min_circularity, orient="horizontal")
        circ_scale.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        circ_scale.bind("<ButtonRelease-1>", lambda e: self.detect_spots())
        ttk.Label(control_frame, textvariable=self.min_circularity).grid(row=1, column=2, padx=5, pady=2, sticky="w")
        
        invert_check = ttk.Checkbutton(control_frame, text="Invert Image", variable=self.invert_image, 
                                      command=self.detect_spots)
        invert_check.grid(row=1, column=3, columnspan=3, padx=5, pady=2, sticky="w")
        
        # Controls - third row
        ttk.Label(control_frame, text="Threshold:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        thresh_min_scale = ttk.Scale(control_frame, from_=0, to=255, variable=self.threshold_min, orient="horizontal")
        thresh_min_scale.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        thresh_min_scale.bind("<ButtonRelease-1>", lambda e: self.detect_spots())
        ttk.Label(control_frame, textvariable=self.threshold_min).grid(row=2, column=2, padx=5, pady=2, sticky="w")
        
        ttk.Label(control_frame, text="to").grid(row=2, column=3, padx=5, pady=2, sticky="w")
        thresh_max_scale = ttk.Scale(control_frame, from_=0, to=255, variable=self.threshold_max, orient="horizontal")
        thresh_max_scale.grid(row=2, column=4, padx=5, pady=2, sticky="ew")
        thresh_max_scale.bind("<ButtonRelease-1>", lambda e: self.detect_spots())
        ttk.Label(control_frame, textvariable=self.threshold_max).grid(row=2, column=5, padx=5, pady=2, sticky="w")
        
        # Controls - fourth row (Lane Analysis)
        ttk.Label(control_frame, text="Number of Lanes:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        lanes_scale = ttk.Scale(control_frame, from_=1, to=10, variable=self.num_lanes, orient="horizontal")
        lanes_scale.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        lanes_scale.bind("<ButtonRelease-1>", lambda e: self.analyze_lanes())
        ttk.Label(control_frame, textvariable=self.num_lanes).grid(row=3, column=2, padx=5, pady=2, sticky="w")
        
        ttk.Label(control_frame, text="Lane Width:").grid(row=3, column=3, padx=5, pady=2, sticky="w")
        lane_width_scale = ttk.Scale(control_frame, from_=10, to=100, variable=self.lane_width, orient="horizontal")
        lane_width_scale.grid(row=3, column=4, padx=5, pady=2, sticky="ew")
        lane_width_scale.bind("<ButtonRelease-1>", lambda e: self.analyze_lanes())
        ttk.Label(control_frame, textvariable=self.lane_width).grid(row=3, column=5, padx=5, pady=2, sticky="w")
        
        # Controls - last row (buttons)
        button_frame = Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=6, padx=5, pady=5, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="Load Image", command=self.load_image).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Detect Spots", command=self.detect_spots).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Analyze Lanes", command=self.analyze_lanes).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Export Data", command=self.export_data).grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Make all columns in control frame evenly sized
        for i in range(6):
            control_frame.columnconfigure(i, weight=1)
        
        # Tree view for spot data
        data_frame = ttk.LabelFrame(self.right_frame, text="Spot Data")
        data_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Create tree with scrollbars
        self.tree_frame = Frame(data_frame)
        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
        columns = ["Spot #", "Lane", "Rf", "Area", "Saturation", "Rel Conc"]
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars for tree
        self.tree_y_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_y_scroll.grid(row=0, column=1, sticky="ns")
        
        self.tree_x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree_x_scroll.grid(row=1, column=0, sticky="ew")
        
        self.tree.configure(yscrollcommand=self.tree_y_scroll.set, xscrollcommand=self.tree_x_scroll.set)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        
        # TLC metadata display
        info_frame = ttk.LabelFrame(self.right_frame, text="TLC Information")
        info_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        self.info_text = ttk.Label(info_frame, text="No spots detected yet")
        self.info_text.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # === Analysis Tab ===
        self.analysis_frame = Frame(self.analysis_tab)
        self.analysis_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.analysis_frame.columnconfigure(0, weight=1)
        self.analysis_frame.rowconfigure(0, weight=1)
        
        # === Calibration Tab ===
        self.calibration_frame = Frame(self.calibration_tab)
        self.calibration_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.calibration_frame.columnconfigure(0, weight=1)
        self.calibration_frame.rowconfigure(0, weight=1)
        
        calibration_controls = ttk.LabelFrame(self.calibration_frame, text="Calibration Settings")
        calibration_controls.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(calibration_controls, text="Define standard spots for concentration calibration").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(calibration_controls, text="Load Reference Standards", 
                  command=self.load_standards).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    
    def load_image(self):
        # Open file dialog to select image
        file_path = filedialog.askopenfilename(
            title="Select TLC Image", 
            filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.tif;*.tiff")]
        )
        
        if not file_path:
            if self.image_path is None:  # If no previous image and user cancels
                # Show a demo image or placeholder
                ttk.Label(self.canvas_frame, text="Please load a TLC image to begin analysis").grid(
                    row=0, column=0, padx=5, pady=5)
            return
            
        self.image_path = file_path
        self.img = cv2.imread(file_path)
        
        if self.img is None:
            ttk.Label(self.canvas_frame, text="Failed to load image").grid(
                row=0, column=0, padx=5, pady=5)
            return
            
        # Display the original image
        self.img_with_labels = self.img.copy()
        self.display_image(self.img_with_labels)
        
        # Update info
        self.info_text.config(text=f"Image loaded: {os.path.basename(file_path)}\n"
                              f"Size: {self.img.shape[1]}x{self.img.shape[0]}")
        
        # Automatically detect spots with default parameters
        self.detect_spots()
    
    def display_image(self, img):
        # Convert OpenCV image to PIL format
        if img is None:
            return
            
        working_img = img.copy()
        if self.invert_image.get():
            working_img = cv2.bitwise_not(working_img)  # Invert image for dark spots on light background
            
        rgb_img = cv2.cvtColor(working_img, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(rgb_img)
        
        # Set initial size
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Handle initial zero size
        if width < 10:
            width = min(800, img.shape[1])
        if height < 10:
            height = min(600, img.shape[0])
        
        # Resize image to fit canvas
        width_ratio = width / img.shape[1]
        height_ratio = height / img.shape[0]
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(img.shape[1] * ratio)
        new_height = int(img.shape[0] * ratio)
        
        resized_image = self.pil_image.resize((new_width, new_height), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized_image)
        
        # Display on canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Bind resize event
        self.canvas.bind("<Configure>", self.resize_image)
    
    def resize_image(self, event=None):
        if not hasattr(self, 'pil_image') or self.pil_image is None:
            return
            
        # Get current canvas size
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
            
        # Calculate ratio to fit image to canvas
        width_ratio = width / self.pil_image.width
        height_ratio = height / self.pil_image.height
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(self.pil_image.width * ratio)
        new_height = int(self.pil_image.height * ratio)
        
        # Resize the image
        resized_image = self.pil_image.resize((new_width, new_height), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
    
    def detect_spots(self):
        if self.img is None:
            return
            
        # Create a copy for processing
        working_img = self.img.copy()
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(working_img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold if specified
        if self.threshold_min.get() < self.threshold_max.get():
            _, thresholded = cv2.threshold(gray, self.threshold_min.get(), 
                                          self.threshold_max.get(), cv2.THRESH_BINARY)
            gray = thresholded
        
        # Invert if needed for detection (regardless of display setting)
        detection_gray = gray
        if self.invert_image.get():
            detection_gray = cv2.bitwise_not(gray)
        
        # Set up the blob detector with TLC-specific parameters
        params = cv2.SimpleBlobDetector_Params()
        
        # Filter by area
        params.filterByArea = True
        params.minArea = self.min_area.get()
        params.maxArea = self.max_area.get()
        
        # Filter by circularity - TLC spots may be less circular
        params.filterByCircularity = True
        params.minCircularity = self.min_circularity.get()
        
        # Filter by color (dark spots)
        params.filterByColor = True
        params.blobColor = 0 if self.invert_image.get() else 255
        
        # Create detector and detect blobs
        detector = cv2.SimpleBlobDetector_create(params)
        self.keypoints = detector.detect(detection_gray)
        
        # Create a fresh copy of the original image for drawing
        self.img_with_labels = self.img.copy()
        
        # Create a DataFrame to store spot information
        self.blob_data = pd.DataFrame(columns=["Spot #", "Lane", "Rf", "X", "Y", 
                                            "Area", "Saturation", "Hue", "Value", 
                                            "Rel Conc"])
        
        # Draw detected spots with labels
        for idx, keypoint in enumerate(self.keypoints):
            x_center, y_center = int(keypoint.pt[0]), int(keypoint.pt[1])
            
            # Handle boundary conditions
            if y_center >= self.img.shape[0] or x_center >= self.img.shape[1]:
                continue
                
            # Draw circles and labels
            radius = int(keypoint.size / 2)
            cv2.circle(self.img_with_labels, (x_center, y_center), radius, (0, 255, 0), 2)
            
            # Draw label above the spot
            label = f"Spot {idx+1}"
            cv2.putText(self.img_with_labels, label, (x_center, y_center-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Extract color and saturation info - key for TLC analysis
            try:
                bgr_color = self.img[y_center, x_center].copy()
                hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
                
                hue, saturation, value = hsv_color[0], hsv_color[1], hsv_color[2]
                
                # Calculate area
                area = np.pi * (keypoint.size/2) ** 2
                
                # For TLC: y-position relative to total height (approximate Rf value)
                rf_value = 1.0 - (y_center / self.img.shape[0])
                
                # Determine lane number based on x-position (if multiple lanes)
                lane_num = 1
                if self.num_lanes.get() > 1:
                    lane_width = self.img.shape[1] / self.num_lanes.get()
                    lane_num = int(x_center / lane_width) + 1
                
                # Store spot information
                new_row = pd.DataFrame({
                    "Spot #": [idx + 1],
                    "Lane": [lane_num],
                    "Rf": [round(rf_value, 3)],
                    "X": [x_center],
                    "Y": [y_center],
                    "Area": [round(area, 2)],
                    "Saturation": [int(saturation)],
                    "Hue": [int(hue)],
                    "Value": [int(value)],
                    "Rel Conc": [round(saturation / 255.0, 3)]  # Simplified relative concentration
                })
                
                self.blob_data = pd.concat([self.blob_data, new_row], ignore_index=True)
            except Exception as e:
                print(f"Error processing spot {idx+1}: {e}")
        
        # Display the image with detected spots
        self.display_image(self.img_with_labels)
        
        # Update the tree view
        self.update_tree_view()
        
        # Update info
        if len(self.keypoints) > 0:
            self.info_text.config(text=f"Detected {len(self.keypoints)} spots\n"
                                f"Parameters: Area: {self.min_area.get()}-{self.max_area.get()}, "
                                f"Circularity: {self.min_circularity.get():.2f}")
        else:
            self.info_text.config(text="No spots detected with current parameters.\n"
                                "Try adjusting the area, circularity, or threshold values.")
        
        # Update analysis tab
        self.create_concentration_plot()
        
        # If we already have lanes set up, update the lane analysis
        if self.num_lanes.get() > 1:
            self.analyze_lanes()
    
    def update_tree_view(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.blob_data is None or len(self.blob_data) == 0:
            return
            
        # Update column widths
        for col in self.tree["columns"]:
            self.tree.column(col, width=80, anchor="center")
        
        # Insert data
        for idx, row in self.blob_data.iterrows():
            values = [
                row["Spot #"],
                row["Lane"],
                row["Rf"],
                int(row["Area"]),
                row["Saturation"],
                row["Rel Conc"]
            ]
            self.tree.insert("", "end", values=values)
    
    def analyze_lanes(self):
        if self.img is None or self.blob_data is None or len(self.blob_data) == 0:
            return
            
        # Create a copy of the image for lane analysis
        lane_img = self.img_with_labels.copy()
        
        # Calculate lane width
        img_width = self.img.shape[1]
        num_lanes = self.num_lanes.get()
        lane_width = img_width // num_lanes
        
        # Draw lane separators
        for i in range(1, num_lanes):
            x_pos = i * lane_width
            cv2.line(lane_img, (x_pos, 0), (x_pos, self.img.shape[0]), (0, 0, 255), 2)
        
        # Display lane numbers
        for i in range(num_lanes):
            x_pos = i * lane_width + lane_width // 2
            cv2.putText(lane_img, f"Lane {i+1}", (x_pos-30, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Display the image with lanes
        self.display_image(lane_img)
        
        # Update lane assignments in blob data
        for idx, row in self.blob_data.iterrows():
            x_pos = row["X"]
            lane_num = min(num_lanes, max(1, int(x_pos / lane_width) + 1))
            self.blob_data.at[idx, "Lane"] = lane_num
        
        # Group spots by lane
        self.lanes = []
        for i in range(1, num_lanes+1):
            lane_spots = self.blob_data[self.blob_data["Lane"] == i]
            self.lanes.append(lane_spots)
        
        # Update the tree view with new lane assignments
        self.update_tree_view()
        
        # Update analysis tab with lane data
        self.create_lane_analysis_plots()
    
    def create_concentration_plot(self):
        # Clear previous plots
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        if self.blob_data is None or len(self.blob_data) == 0:
            ttk.Label(self.analysis_frame, text="No spot data available for analysis").grid(
                row=0, column=0, padx=5, pady=5)
            return
        
        # Create concentration analysis plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        
        # Plot 1: Rf vs Saturation (proxy for concentration)
        ax1.scatter(self.blob_data["Rf"], self.blob_data["Saturation"], 
                   s=self.blob_data["Area"]/10, alpha=0.7)
        ax1.set_xlabel("Rf Value")
        ax1.set_ylabel("Saturation (Concentration)")
        ax1.set_title("Rf vs Concentration")
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Label each point with spot number
        for i, row in self.blob_data.iterrows():
            ax1.annotate(f"{int(row['Spot #'])}", 
                        (row["Rf"], row["Saturation"]),
                        fontsize=8)
        
        # Plot 2: Spot size vs Saturation
        ax2.scatter(self.blob_data["Area"], self.blob_data["Saturation"], 
                   c=self.blob_data["Hue"], cmap="hsv", alpha=0.7)
        ax2.set_xlabel("Spot Area")
        ax2.set_ylabel("Saturation (Concentration)")
        ax2.set_title("Area vs Concentration")
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed matplotlib figure in tkinter
        plot_frame = ttk.LabelFrame(self.analysis_frame, text="Concentration Analysis")
        plot_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add statistics summary
        stats_frame = ttk.LabelFrame(self.analysis_frame, text="Statistical Summary")
        stats_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Calculate statistics
        mean_sat = self.blob_data["Saturation"].mean()
        max_sat = self.blob_data["Saturation"].max()
        mean_area = self.blob_data["Area"].mean()
        
        # Display statistics
        stats_text = (f"Mean Saturation: {mean_sat:.2f}\n"
                     f"Max Saturation: {max_sat:.2f}\n"
                     f"Mean Spot Area: {mean_area:.2f}")
        
        ttk.Label(stats_frame, text=stats_text).pack(padx=5, pady=5)
    
    def create_lane_analysis_plots(self):
        if not self.lanes or len(self.lanes) == 0:
            return
            
        # Create new frame in analysis tab
        lane_frame = ttk.LabelFrame(self.analysis_frame, text="Lane Analysis")
        lane_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create a plot of concentration profiles by lane
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Plot concentration vs Rf for each lane
        lane_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        for i, lane_data in enumerate(self.lanes):
            if len(lane_data) > 0:
                color = lane_colors[i % len(lane_colors)]
                ax.scatter(lane_data["Rf"], lane_data["Saturation"], 
                          label=f"Lane {i+1}", color=color, alpha=0.7)
                
                # Add trend line
                if len(lane_data) > 1:
                    try:
                        # Sort data by Rf for proper line plotting
                        sorted_data = lane_data.sort_values("Rf")
                        ax.plot(sorted_data["Rf"], sorted_data["Saturation"], 
                              '--', color=color, alpha=0.5)
                    except:
                        pass
        
        ax.set_xlabel("Rf Value")
        ax.set_ylabel("Saturation (Concentration)")
        ax.set_title("Concentration Profile by Lane")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        plt.tight_layout()
        
        # Embed matplotlib figure in tkinter
        canvas = FigureCanvasTkAgg(fig, master=lane_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def load_standards(self):
        # This function would allow loading standard spots with known concentrations
        # for calibration purposes. For now, it's a placeholder.
        ttk.Label(self.calibration_frame, text="Calibration feature is under development").grid(
            row=1, column=0, padx=5, pady=5)
    
    def export_data(self):
        if self.blob_data is None or len(self.blob_data) == 0:
            return
            
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            title="Save TLC Analysis Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if not file_path:
            return
            
        # Export the data
        if file_path.endswith(".csv"):
            self.blob_data.to_csv(file_path, index=False)
        elif file_path.endswith(".xlsx"):
            self.blob_data.to_excel(file_path, index=False)
        
        # Inform user
        self.info_text.config(text=f"Data exported to {os.path.basename(file_path)}")

if __name__ == "__main__":
    root = Tk()
    app = TLCAnalyzer(root)
    root.mainloop()
