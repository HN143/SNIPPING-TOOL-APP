import sys
from os.path import basename
from PyQt6.QtCore import QPoint, Qt, QRect
from PyQt6.QtWidgets import QMainWindow , QPushButton, QMenu, QFileDialog
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt6.QtGui import QAction

import SnippingTool


class Menu(QMainWindow):
    COLORS = ['Red', 'Black', 'Blue', 'Green', 'Yellow']
    SIZES = [1, 3, 5, 7, 9, 11]
    default_title = "Snipping Tool"

    def __init__(self, numpy_image=None, snip_number=None, start_position=(300, 300, 350, 250)):
        super().__init__()

        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.GlobalColor.red
        self.lastPoint = QPoint()
        self.total_snips = 0
        self.title = Menu.default_title

        # New snip
        new_snip_action = QAction('New', self)
        new_snip_action.setShortcut('Ctrl+N')
        new_snip_action.setStatusTip('Snip!')
        new_snip_action.triggered.connect(self.new_image_window)

        # Brush color
        brush_color_button = QPushButton("Brush Color")
        colorMenu = QMenu()
        for color in Menu.COLORS:
            colorMenu.addAction(color)
        brush_color_button.setMenu(colorMenu)
        colorMenu.triggered.connect(lambda action: change_brush_color(action.text()))

        # Brush Size
        brush_size_button = QPushButton("Brush Size")
        sizeMenu = QMenu()
        for size in Menu.SIZES:
            sizeMenu.addAction(f"{size}px")
        brush_size_button.setMenu(sizeMenu)
        sizeMenu.triggered.connect(lambda action: change_brush_size(action.text()))

        # Save
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save')
        save_action.triggered.connect(self.save_file)

        # Exit
        exit_window = QAction('Exit', self)
        exit_window.setShortcut('Ctrl+Q')
        exit_window.setStatusTip('Exit application')
        exit_window.triggered.connect(self.close)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(new_snip_action)
        self.toolbar.addAction(save_action)
        self.toolbar.addWidget(brush_color_button)
        self.toolbar.addWidget(brush_size_button)
        self.toolbar.addAction(exit_window)

        self.snippingTool = SnippingTool.SnippingWidget()
        self.setGeometry(*start_position)

        if numpy_image is not None and snip_number is not None:
            self.image = self.convert_numpy_img_to_qpixmap(numpy_image)
            self.change_and_set_title(f"Snip #{snip_number}")
        else:
            self.image = QPixmap("background.PNG")
            self.change_and_set_title(Menu.default_title)

        self.resize(self.image.width(), self.image.height() + self.toolbar.height())
        self.show()

        def change_brush_color(new_color):
            self.brushColor = getattr(Qt.GlobalColor, new_color.lower())

        def change_brush_size(new_size):
            self.brushSize = int(''.join(filter(str.isdigit, new_size)))

    def new_image_window(self):
        if self.snippingTool.background:
            self.close()
        self.total_snips += 1
        self.snippingTool.start()

    def save_file(self):
        file_path, name = QFileDialog.getSaveFileName(self, "Save file", self.title, "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved')

    def change_and_set_title(self, new_title):
        self.title = new_title
        self.setWindowTitle(self.title)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = QRect(0, self.toolbar.height(), self.image.width(), self.image.height())
        painter.drawPixmap(rect, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.lastPoint = event.position().toPoint() - QPoint(0, self.toolbar.height())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint, event.position().toPoint() - QPoint(0, self.toolbar.height()))
            self.lastPoint = event.position().toPoint() - QPoint(0, self.toolbar.height())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def closeEvent(self, event):
        event.accept()

    @staticmethod
    def convert_numpy_img_to_qpixmap(np_img):
        height, width, channel = np_img.shape
        bytesPerLine = 3 * width
        return QPixmap(QImage(np_img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped())


if __name__ == '__main__':
    mainMenu = Menu()
    app = QApplication([])
    sys.exit(app.exec())
