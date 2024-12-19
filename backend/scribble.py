from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QSlider, QHBoxLayout
from PyQt5.QtGui import QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint


###
# ScribbleArea class
# This class is responsible for drawing on the image
# It also saves the annotations and creates the mask
###

class ScribbleArea(QLabel):
    def __init__(self):
        super().__init__()
        self.brushSize = 5
        self.brushColor = Qt.black
        self.drawing_ignore = False
        self.lastPoint = QPoint()
        self.image = QImage()  # RGB image
        self.white_canvas = QImage()  # the white canvas fro annotating
        self.ignore_canvas = QImage()

    def load_image(self, fileName):

        self.image.load(fileName)

        # Create a white canvas of the same size for annotations
        self.white_canvas = QImage(self.image.size(), QImage.Format_RGB32)
        self.white_canvas.fill(Qt.white)

        # Create a white canvas of the same size for the ignore region
        self.ignore_canvas = QImage(self.image.size(), QImage.Format_RGB32)
        self.ignore_canvas.fill(Qt.white)

        self.update()
        return True

    def setBrushSize(self, size):
        self.brushSize = size

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):

        # painter for the RGB image
        painter = QPainter(self.image)
        painter.setPen(QPen(self.brushColor, self.brushSize,
                       Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, event.pos())

        # white canvas for annotations
        white_painter = QPainter(self.white_canvas)
        white_painter.setPen(
            QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        white_painter.drawLine(self.lastPoint, event.pos())

        # Draw on the ignore canvas as well
        ignore_painter = QPainter(self.ignore_canvas)
        ignore_painter.setPen(
            QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        ignore_painter.drawLine(self.lastPoint, event.pos())

        self.lastPoint = event.pos()
        self.update()

    def setIgnoreMode(self, ignore):
        self.drawing_ignore = ignore
        self.brushColor = Qt.green if ignore else Qt.black

    def create_mask(self, anotated_image_path, output_path_ignore_annotations_path):

        # find the anotated image and load with QImage
        annotated_image = QImage()
        annotated_image.load(anotated_image_path)

        # find the ignore anotated image and load with QImage
        ignore_annotated_image = QImage()
        ignore_annotated_image.load(output_path_ignore_annotations_path)

        # create a black image
        self.mask_image = QImage(self.image.size(), QImage.Format_RGB32)
        self.ignore_mask_image = QImage(self.image.size(), QImage.Format_RGB32)

        # Iterate through the canvas_with_annotations_qimage
        for y in range(annotated_image.height()):
            for x in range(annotated_image.width()):
                # Check if the pixel is green, this would mean its an ignored region
                if annotated_image.pixelColor(x, y) == QColor(0, 255, 0):
                    # Set mask pixel to white
                    self.ignore_mask_image.setPixelColor(x, y, QColor(
                        255, 255, 255))

                # Check if the pixel is white
                # that means no annotation was made, so we ignore it for both masks
                elif annotated_image.pixelColor(x, y) == QColor(255, 255, 255):
                    # Set mask pixel to black
                    self.mask_image.setPixelColor(x, y, QColor(
                        0, 0, 0))
                    self.ignore_mask_image.setPixelColor(x, y, QColor(0, 0, 0))

                else:  # default to white in main mask
                    self.mask_image.setPixelColor(x, y, QColor(
                        255, 255, 255))

        # save the mask
        self.mask_image.save(anotated_image_path.replace(
            '_annotations.png', '_mask.png'), format='PNG')
        self.ignore_mask_image.save(anotated_image_path.replace(
            '_annotations.png', '_ignore_mask.png'), format='PNG')

    def saveImage(self, output_path):
        print('Saving image with scribbles')

        output_path_with_scribbles = output_path.replace(
            '.png', '_with_scribbles.png')
        self.image.save(output_path_with_scribbles, format='PNG')

        output_path_annotations = output_path.replace(
            '.png', '_annotations.png')
        self.white_canvas.save(output_path_annotations, format='PNG')
        # self.transparent_canvas.save(output_path_annotations, format='PNG')

        output_path_ignore_annotations = output_path.replace(
            '.png', '_ignore_annotations.png')
        # self.ignore_canvas.save(output_path_ignore_annotations, format='PNG')

        self.create_mask(output_path_annotations,
                         output_path_ignore_annotations)


class MainWindow(QMainWindow):
    def __init__(self, image_path, output_path, image_file):
        super().__init__()

        self.setWindowTitle("Depth Annotation Application")
        self.setGeometry(200, 200, 600, 600)
        self.image_path = image_path+image_file
        self.output_path = output_path+image_file

        self.scribble_area = ScribbleArea()
        self.scribble_area.load_image(
            self.image_path)

        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.saveImage)
        # buttons to toggle ignored regions drawing
        self.ignore_button = QPushButton("Set Ignore Pen")
        self.annotate_button = QPushButton("Set Annotation Pen")
        self.ignore_button.clicked.connect(self.toggleIgnoreMode)
        self.annotate_button.clicked.connect(
            self.toggleAnnotationMode)

        # brush size slider and labels
        self.brush_size_slider_label = QLabel("Brush Size: 3")
        self.brush_size_slider = QSlider(Qt.Vertical)
        self.brush_size_slider.setMinimum(3)
        self.brush_size_slider.setMaximum(20)
        self.brush_size_slider.setValue(5)
        self.brush_size_slider.valueChanged.connect(self.changeBrushSize)

        # Slider for changing brush color (gray-scale)
        self.brush_slider_label = QLabel("Brush Colour (gray-scale)")
        self.brush_slider = QSlider(Qt.Vertical)
        self.brush_slider.setMinimum(0)
        self.brush_slider.setMaximum(255)
        self.brush_slider.setValue(25)
        self.brush_slider.valueChanged.connect(self.changeBrushColor)

        # Depth annotation label that will be updated by the slider
        self.depth_annotation_label = QLabel("Depth Annotation: 25")
        self.brush_slider.valueChanged.connect(self.updateDepthAnnotationLabel)

        # Slider and label layout for depth and brush size
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.depth_annotation_label)
        slider_layout.addWidget(self.brush_slider_label)
        slider_layout.addWidget(self.brush_slider)
        slider_layout.addWidget(self.brush_size_slider_label)
        slider_layout.addWidget(self.brush_size_slider)

        # Main layout with scribble area and sliders
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.scribble_area)
        main_layout.addLayout(slider_layout)

        layout = QVBoxLayout()
        layout.addLayout(main_layout)
        layout.addWidget(self.ignore_button)
        layout.addWidget(self.annotate_button)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # Switch the mode and brush color for ignored regions
    def toggleIgnoreMode(self):
        self.scribble_area.setIgnoreMode(True)
        self.ignore_button.setEnabled(False)
        self.annotate_button.setEnabled(True)

    def toggleAnnotationMode(self):
        self.scribble_area.setIgnoreMode(False)
        self.ignore_button.setEnabled(True)
        self.annotate_button.setEnabled(False)

    def updateDepthAnnotationLabel(self, value):
        self.depth_annotation_label.setText(f"Depth Annotation: {value}")

    def changeBrushSize(self, value):
        self.scribble_area.setBrushSize(value)
        self.brush_size_value = value
        self.brush_size_slider_label.setText(f"Brush Size: {value}")

    def changeBrushColor(self, value):
        # Change the brush color based on the slider value
        self.scribble_area.brushColor = QColor(value, value, value)

    def saveImage(self):
        print('Saving image')
        print(self.image_path)
        self.scribble_area.saveImage(self.output_path)
