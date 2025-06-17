import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QTextEdit, QFileDialog, QHBoxLayout, QMessageBox, QRubberBand,
    QDesktopWidget, QToolBar, QAction, QColorDialog, QSpinBox, QDialog,
    QDialogButtonBox, QInputDialog, QButtonGroup, QLineEdit, QFrame
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont, QColor, QIcon, QBrush, QPalette
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QTimer, QEventLoop, pyqtSignal
from PIL import ImageGrab, Image
import math
try:
    from PIL.ImageQt import ImageQt
except ImportError:
    try:
        from PIL import ImageQt
    except ImportError:
        ImageQt = None
from fpdf import FPDF
import time


current_dir = os.path.dirname(os.path.abspath(__file__))
folders = ['images', 'templates']

for folder in folders:
    folder_path = os.path.join(current_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def pil_to_qpixmap(pil_image):
    """Converte imagem PIL para QPixmap de forma compatível"""
    if ImageQt:
        try:
            return QPixmap.fromImage(ImageQt(pil_image))
        except:
            pass
    
    # Fallback: salvar temporariamente
    temp_path = f"temp_image_{int(time.time())}.png"
    pil_image.save(temp_path)
    pixmap = QPixmap(temp_path)
    try:
        os.remove(temp_path)
    except:
        pass
    return pixmap

class Step:
    def __init__(self, image_path, description):
        self.image_path = image_path
        self.description = description

class CoverDialog(QDialog):
    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Capa")
        self.setModal(True)
        
        # Configurar estilo moderno
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #424242;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("📑 Título:")
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Digite o título da documentação")
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)
        
        # Descrição
        desc_label = QLabel("📝 Descrição:")
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Digite a descrição da documentação")
        self.desc_edit.setText(description)
        self.desc_edit.setMinimumHeight(100)
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_edit)
        
        # Botões
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        ok_button = QPushButton("✅ Salvar")
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.resize(500, 400)

class ImageEditor(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("Editor de Imagem")
        self.setModal(True)
        
        # Configurar estilo moderno
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial;
            }
            QToolBar {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px;
                spacing: 4px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLabel {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QSpinBox {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        # Carregar imagem
        self.original_pixmap = QPixmap(image_path)
        self.edited_pixmap = self.original_pixmap.copy()
        
        # Configurações de desenho
        self.current_tool = "pen"
        self.pen_color = QColor(255, 0, 0)  # Vermelho
        self.pen_width = 3
        self.drawing = False
        self.last_point = QPoint()
        self.start_point = QPoint()
        self.font_size = 12  # Tamanho padrão da fonte
        
        # Histórico para desfazer
        self.history = [self.edited_pixmap.copy()]
        self.history_index = 0
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Label para mostrar imagem
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setMinimumSize(600, 400)
        self.update_image_display()
        layout.addWidget(self.image_label)
        
        # Botões
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save_image)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.resize(800, 700)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Grupo de ferramentas
        tool_group = QButtonGroup(self)
        
        # Estilo para botões de ferramenta
        tool_button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                color: #424242;
            }
            QPushButton:checked {
                background-color: #E3F2FD;
                border-color: #2196F3;
                color: #1976D2;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """
        
        # Ferramenta Caneta
        pen_action = QAction("✏️ Caneta", self)
        pen_action.setCheckable(True)
        pen_action.setChecked(True)
        pen_action.triggered.connect(lambda: self.set_tool("pen"))
        toolbar.addAction(pen_action)
        tool_group.addButton(toolbar.widgetForAction(pen_action))
        
        # Ferramenta Linha
        line_action = QAction("📏 Linha", self)
        line_action.setCheckable(True)
        line_action.triggered.connect(lambda: self.set_tool("line"))
        toolbar.addAction(line_action)
        tool_group.addButton(toolbar.widgetForAction(line_action))
        
        # Ferramenta Retângulo
        rect_action = QAction("⬜ Retângulo", self)
        rect_action.setCheckable(True)
        rect_action.triggered.connect(lambda: self.set_tool("rectangle"))
        toolbar.addAction(rect_action)
        tool_group.addButton(toolbar.widgetForAction(rect_action))
        
        # Ferramenta Seta
        arrow_action = QAction("➡️ Seta", self)
        arrow_action.setCheckable(True)
        arrow_action.triggered.connect(lambda: self.set_tool("arrow"))
        toolbar.addAction(arrow_action)
        tool_group.addButton(toolbar.widgetForAction(arrow_action))
        
        # Ferramenta Texto
        text_action = QAction("🔤 Texto", self)
        text_action.setCheckable(True)
        text_action.triggered.connect(lambda: self.set_tool("text"))
        toolbar.addAction(text_action)
        tool_group.addButton(toolbar.widgetForAction(text_action))
        
        toolbar.addSeparator()
        
        # Cor
        color_btn = QPushButton("🎨 Cor")
        color_btn.clicked.connect(self.choose_color)
        color_btn.setStyleSheet(tool_button_style)
        toolbar.addWidget(color_btn)
        
        # Espessura
        toolbar.addWidget(QLabel("Espessura:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20)
        self.width_spin.setValue(3)
        self.width_spin.valueChanged.connect(self.set_pen_width)
        toolbar.addWidget(self.width_spin)
        
        # Tamanho da fonte (apenas quando a ferramenta texto está selecionada)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Tamanho do Texto:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.font_size)
        self.font_size_spin.valueChanged.connect(self.set_font_size)
        self.font_size_spin.setEnabled(False)  # Inicialmente desabilitado
        toolbar.addWidget(self.font_size_spin)
        
        toolbar.addSeparator()
        
        # Desfazer
        undo_action = QAction("↶ Desfazer", self)
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)
        
        # Limpar
        clear_action = QAction("🗑️ Limpar", self)
        clear_action.triggered.connect(self.clear_all)
        toolbar.addAction(clear_action)
        
        return toolbar
        
    def set_tool(self, tool):
        self.current_tool = tool
        # Habilitar/desabilitar controle de tamanho da fonte
        self.font_size_spin.setEnabled(tool == "text")
        
    def choose_color(self):
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color
            
    def set_pen_width(self, width):
        self.pen_width = width
        
    def set_font_size(self, size):
        self.font_size = size
        
    def update_image_display(self):
        # Redimensionar imagem para caber na tela
        scaled_pixmap = self.edited_pixmap.scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Converter coordenadas da tela para coordenadas da imagem
            label_pos = self.image_label.mapFromGlobal(event.globalPos())
            if self.image_label.rect().contains(label_pos):
                # Calcular posição na imagem original
                label_rect = self.image_label.rect()
                pixmap_rect = self.image_label.pixmap().rect()
                
                # Calcular escala
                scale_x = self.edited_pixmap.width() / pixmap_rect.width()
                scale_y = self.edited_pixmap.height() / pixmap_rect.height()
                
                # Calcular offset para centralização
                offset_x = (label_rect.width() - pixmap_rect.width()) / 2
                offset_y = (label_rect.height() - pixmap_rect.height()) / 2
                
                # Posição na imagem
                img_x = int((label_pos.x() - offset_x) * scale_x)
                img_y = int((label_pos.y() - offset_y) * scale_y)
                
                self.start_point = QPoint(img_x, img_y)
                self.last_point = QPoint(img_x, img_y)
                self.drawing = True
                
                if self.current_tool == "text":
                    self.add_text(img_x, img_y)
                    
    def mouseMoveEvent(self, event):
        if self.drawing and self.current_tool == "pen":
            label_pos = self.image_label.mapFromGlobal(event.globalPos())
            if self.image_label.rect().contains(label_pos):
                # Calcular posição na imagem
                label_rect = self.image_label.rect()
                pixmap_rect = self.image_label.pixmap().rect()
                
                scale_x = self.edited_pixmap.width() / pixmap_rect.width()
                scale_y = self.edited_pixmap.height() / pixmap_rect.height()
                
                offset_x = (label_rect.width() - pixmap_rect.width()) / 2
                offset_y = (label_rect.height() - pixmap_rect.height()) / 2
                
                img_x = int((label_pos.x() - offset_x) * scale_x)
                img_y = int((label_pos.y() - offset_y) * scale_y)
                
                current_point = QPoint(img_x, img_y)
                self.draw_line(self.last_point, current_point)
                self.last_point = current_point
                
    def mouseReleaseEvent(self, event):
        if self.drawing and event.button() == Qt.LeftButton:
            label_pos = self.image_label.mapFromGlobal(event.globalPos())
            if self.image_label.rect().contains(label_pos):
                # Calcular posição final
                label_rect = self.image_label.rect()
                pixmap_rect = self.image_label.pixmap().rect()
                
                scale_x = self.edited_pixmap.width() / pixmap_rect.width()
                scale_y = self.edited_pixmap.height() / pixmap_rect.height()
                
                offset_x = (label_rect.width() - pixmap_rect.width()) / 2
                offset_y = (label_rect.height() - pixmap_rect.height()) / 2
                
                img_x = int((label_pos.x() - offset_x) * scale_x)
                img_y = int((label_pos.y() - offset_y) * scale_y)
                
                end_point = QPoint(img_x, img_y)
                
                if self.current_tool == "line":
                    self.draw_line(self.start_point, end_point)
                elif self.current_tool == "rectangle":
                    self.draw_rectangle(self.start_point, end_point)
                elif self.current_tool == "arrow":
                    self.draw_arrow(self.start_point, end_point)
                    
            self.drawing = False
            self.save_to_history()
            
    def draw_line(self, start, end):
        painter = QPainter(self.edited_pixmap)
        painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
        painter.drawLine(start, end)
        painter.end()
        self.update_image_display()
        
    def draw_rectangle(self, start, end):
        painter = QPainter(self.edited_pixmap)
        painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
        rect = QRect(start, end).normalized()
        painter.drawRect(rect)
        painter.end()
        self.update_image_display()
        
    def draw_arrow(self, start, end):
        painter = QPainter(self.edited_pixmap)
        painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine))
        painter.setBrush(QBrush(self.pen_color))
        
        # Desenhar linha principal
        painter.drawLine(start, end)
        
        # Calcular pontos da seta
        angle = math.atan2((end.y() - start.y()), (end.x() - start.x()))
        
        # Tamanho da ponta da seta
        arrow_length = 15
        arrow_angle = 0.5
        
        # Pontos da seta
        arrow_p1 = QPoint(
            int(end.x() - arrow_length * math.cos(angle - arrow_angle)),
            int(end.y() - arrow_length * math.sin(angle - arrow_angle))
        )
        arrow_p2 = QPoint(
            int(end.x() - arrow_length * math.cos(angle + arrow_angle)),
            int(end.y() - arrow_length * math.sin(angle + arrow_angle))
        )
        
        # Desenhar ponta da seta
        painter.drawLine(end, arrow_p1)
        painter.drawLine(end, arrow_p2)
        
        painter.end()
        self.update_image_display()
        
    def add_text(self, x, y):
        text, ok = QInputDialog.getText(self, "Adicionar Texto", "Digite o texto:")
        if ok and text:
            painter = QPainter(self.edited_pixmap)
            painter.setPen(QPen(self.pen_color))
            font = QFont("Segoe UI", self.font_size)
            painter.setFont(font)
            painter.drawText(x, y, text)
            painter.end()
            self.update_image_display()
            self.save_to_history()
            
    def save_to_history(self):
        # Remover histórico futuro se estamos no meio
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            
        # Adicionar novo estado
        self.history.append(self.edited_pixmap.copy())
        self.history_index += 1
        
        # Limitar histórico
        if len(self.history) > 20:
            self.history.pop(0)
            self.history_index -= 1
            
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.edited_pixmap = self.history[self.history_index].copy()
            self.update_image_display()
            
    def clear_all(self):
        reply = QMessageBox.question(self, "Limpar", "Deseja limpar todas as edições?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.edited_pixmap = self.original_pixmap.copy()
            self.update_image_display()
            self.save_to_history()
            
    def save_image(self):
        self.edited_pixmap.save(self.image_path)
        self.accept()

class RegionSelector(QWidget):
    selection_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Configurar para tela cheia
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(screen_rect)
        
        # Capturar screenshot
        self.screenshot = ImageGrab.grab()
        self.pixmap = pil_to_qpixmap(self.screenshot)
        
        # Variáveis para seleção
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selecting = False
        self.selected_rect = QRect()
        
        # Configurar cursor
        self.setCursor(Qt.CrossCursor)
        
        # Mostrar instruções
        self.show_instructions = True
        
        # Configurar estilo
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Desenhar o screenshot
        painter.drawPixmap(self.rect(), self.pixmap)
        
        # Desenhar overlay escuro com efeito de gradiente
        overlay_color = QColor(0, 0, 0, 100)  # Preto com transparência
        painter.fillRect(self.rect(), overlay_color)
        
        # Se estamos selecionando, desenhar retângulo
        if self.selecting and not self.start_point.isNull() and not self.end_point.isNull():
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Desenhar área selecionada sem overlay
            painter.drawPixmap(selection_rect, self.pixmap, selection_rect)
            
            # Desenhar borda da seleção com efeito de brilho
            pen = QPen(QColor(33, 150, 243), 2, Qt.SolidLine)  # Azul Material Design
            painter.setPen(pen)
            painter.drawRect(selection_rect)
            
            # Desenhar dimensões
            dimensions = f"{selection_rect.width()} x {selection_rect.height()}"
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255)))
            
            # Desenhar fundo para o texto
            text_rect = painter.fontMetrics().boundingRect(dimensions)
            text_rect.moveTop(selection_rect.top() - text_rect.height() - 5)
            text_rect.moveLeft(selection_rect.left())
            painter.fillRect(text_rect, QColor(33, 150, 243, 200))
            
            # Desenhar texto
            painter.drawText(text_rect, Qt.AlignCenter, dimensions)
        
        # Desenhar instruções com estilo moderno
        if self.show_instructions:
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
            
            # Desenhar fundo para as instruções
            instruction_text = "Clique e arraste para selecionar uma área da tela. Pressione ESC para cancelar."
            text_rect = painter.fontMetrics().boundingRect(instruction_text)
            text_rect.moveTop(20)
            text_rect.moveLeft(20)
            text_rect.adjust(-10, -5, 10, 5)  # Adicionar padding
            
            # Desenhar fundo com efeito de vidro
            painter.fillRect(text_rect, QColor(0, 0, 0, 150))
            painter.drawRect(text_rect)
            
            # Desenhar texto
            painter.drawText(30, 40, instruction_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.selecting = True
            self.show_instructions = False
            self.update()

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selecting:
            self.end_point = event.pos()
            self.selected_rect = QRect(self.start_point, self.end_point).normalized()
            self.selecting = False
            self.selection_finished.emit()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.selected_rect = QRect()  # Cancelar seleção
            self.selection_finished.emit()
            self.close()
    
    def closeEvent(self, event):
        self.selection_finished.emit()
        super().closeEvent(event)

class DocCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Documentação")
        self.steps = []
        self.doc_title = "Documentação de Processo"
        self.doc_description = ""
        
        # Configurar estilo moderno
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: #424242;
                font-weight: bold;
            }
        """)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Layout dos botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Estilo específico para cada botão
        button_styles = {
            "add": "background-color: #4CAF50;",
            "edit": "background-color: #2196F3;",
            "delete": "background-color: #F44336;",
            "pdf": "background-color: #9C27B0;",
            "save_template": "background-color: #FF9800;",
            "load_template": "background-color: #795548;",
            "rename": "background-color: #607D8B;",
            "edit_cover": "background-color: #673AB7;"
        }
        
        # Criar botões com tamanho mínimo
        self.add_btn = QPushButton("➕ Adicionar")
        self.edit_btn = QPushButton("✏️ Editar")
        self.delete_btn = QPushButton("🗑️ Deletar")
        self.pdf_btn = QPushButton("📄 PDF")
        save_template_btn = QPushButton("💾 Salvar")
        load_template_btn = QPushButton("📂 Carregar")
        self.rename_btn = QPushButton("✏️ Renomear")
        edit_cover_btn = QPushButton("📑 Capa")
        
        # Aplicar estilos específicos e tamanho mínimo
        for btn, style in [
            (self.add_btn, button_styles["add"]),
            (self.edit_btn, button_styles["edit"]),
            (self.delete_btn, button_styles["delete"]),
            (self.pdf_btn, button_styles["pdf"]),
            (save_template_btn, button_styles["save_template"]),
            (load_template_btn, button_styles["load_template"]),
            (self.rename_btn, button_styles["rename"]),
            (edit_cover_btn, button_styles["edit_cover"])
        ]:
            btn.setMinimumWidth(100)  # Definir largura mínima
            btn.setStyleSheet(f"""
                QPushButton {{
                    {style}
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {style.split(':')[1].strip()[:-1]}CC;
                }}
                QPushButton:pressed {{
                    background-color: {style.split(':')[1].strip()[:-1]}99;
                }}
            """)
        
        # Conectar sinais
        self.add_btn.clicked.connect(self.add_step)
        self.edit_btn.clicked.connect(self.edit_image)
        self.delete_btn.clicked.connect(self.delete_step)
        self.pdf_btn.clicked.connect(self.generate_pdf)
        save_template_btn.clicked.connect(self.save_template)
        load_template_btn.clicked.connect(self.load_template)
        self.rename_btn.clicked.connect(self.edit_step_name)
        edit_cover_btn.clicked.connect(self.edit_cover)
        
        # Adicionar botões ao layout com quebra de linha
        first_row = QHBoxLayout()
        second_row = QHBoxLayout()
        
        # Primeira linha de botões
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.rename_btn]:
            first_row.addWidget(btn)
        
        # Segunda linha de botões
        for btn in [self.pdf_btn, save_template_btn, load_template_btn, edit_cover_btn]:
            second_row.addWidget(btn)
        
        # Adicionar as duas linhas ao layout principal
        main_layout.addLayout(first_row)
        main_layout.addLayout(second_row)
        
        # Lista de etapas com estilo moderno
        steps_label = QLabel("📋 Etapas:")
        steps_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        
        self.step_list = QListWidget()
        self.step_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        self.step_list.itemClicked.connect(self.display_step)
        self.step_list.setMaximumHeight(150)
        
        # Visualização da imagem com estilo moderno
        image_label = QLabel("🖼️ Imagem:")
        image_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        
        self.image_label = QLabel("Nenhuma imagem selecionada")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #E0E0E0;
                border-radius: 4px;
                padding: 20px;
                min-height: 200px;
            }
        """)
        
        # Editor de descrição com estilo moderno
        desc_label = QLabel("📝 Descrição da etapa:")
        desc_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Digite a descrição desta etapa...")
        self.desc_edit.textChanged.connect(self.update_description)
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Adicionar widgets ao layout principal
        main_layout.addWidget(steps_label)
        main_layout.addWidget(self.step_list)
        main_layout.addWidget(image_label)
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(desc_label)
        main_layout.addWidget(self.desc_edit)
        
        # Configurar tamanho mínimo da janela
        self.setMinimumSize(800, 700)

    def add_step(self):
        try:
            # Minimizar a janela principal
            self.showMinimized()
            
            # Aguardar um pouco para a janela minimizar
            QTimer.singleShot(500, self.capture_screen)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar etapa: {str(e)}")
            self.showNormal()

    def capture_screen(self):
        try:
            selector = RegionSelector()
            loop = QEventLoop()
            selector.selection_finished.connect(loop.quit)
            selector.show()
            loop.exec_()
            
            if not selector.selected_rect.isEmpty():
                rect = selector.selected_rect
                crop_box = (rect.x(), rect.y(), 
                           rect.x() + rect.width(), 
                           rect.y() + rect.height())
                
                step_img = selector.screenshot.crop(crop_box)
                
                # Criar pasta 'images' se não existir
                images_dir = os.path.join(os.path.dirname(__file__), 'images')
                os.makedirs(images_dir, exist_ok=True)
                
                # Salvar imagem na pasta 'images'
                img_path = os.path.join(images_dir, f"step_{len(self.steps) + 1}.png")
                step_img.save(img_path)
                
                # Criar nova etapa com nome personalizável
                text, ok = QInputDialog.getText(
                    self, 
                    "Nome da Etapa", 
                    "Digite o nome da etapa:",
                    QLineEdit.Normal,
                    f"Etapa {len(self.steps) + 1}"
                )
                if not ok:
                    text = f"Etapa {len(self.steps) + 1}"
                
                step = Step(img_path, "")
                self.steps.append(step)
                
                item = QListWidgetItem(text)
                self.step_list.addItem(item)
                self.step_list.setCurrentItem(item)
                
                self.display_step(item)
    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao capturar tela: {str(e)}")
        
        finally:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def edit_image(self):
        current_item = self.step_list.currentItem()
        if current_item:
            row = self.step_list.row(current_item)
            if row < len(self.steps):
                step = self.steps[row]
                if os.path.exists(step.image_path):
                    editor = ImageEditor(step.image_path, self)
                    if editor.exec_() == QDialog.Accepted:
                        # Atualizar visualização
                        self.display_step(current_item)
                        QMessageBox.information(self, "Sucesso", "Imagem editada com sucesso!")
                else:
                    QMessageBox.warning(self, "Erro", "Arquivo de imagem não encontrado!")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma etapa para editar!")

    def delete_step(self):
        current_item = self.step_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Confirmar", 
                                       "Tem certeza que deseja deletar esta etapa?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                row = self.step_list.row(current_item)
                
                # Deletar arquivo de imagem
                try:
                    os.remove(self.steps[row].image_path)
                except:
                    pass
                
                # Remover da lista
                del self.steps[row]
                self.step_list.takeItem(row)
                
                # Limpar visualização se não há mais itens
                if not self.steps:
                    self.image_label.clear()
                    self.image_label.setText("Nenhuma imagem selecionada")
                    self.desc_edit.clear()

    def update_description(self):
        current_item = self.step_list.currentItem()
        if current_item:
            row = self.step_list.row(current_item)
            if row < len(self.steps):
                self.steps[row].description = self.desc_edit.toPlainText()

    def display_step(self, item):
        try:
            row = self.step_list.row(item)
            if row < len(self.steps):
                step = self.steps[row]
                
                # Carregar e exibir imagem
                if os.path.exists(step.image_path):
                    pixmap = QPixmap(step.image_path)
                    # Redimensionar mantendo proporção
                    scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(scaled_pixmap)
                else:
                    self.image_label.setText("Imagem não encontrada")
                
                # Carregar descrição
                self.desc_edit.blockSignals(True)
                self.desc_edit.setText(step.description)
                self.desc_edit.blockSignals(False)
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao exibir etapa: {str(e)}")

    def generate_pdf(self):
        if not self.steps:
            QMessageBox.warning(self, "Aviso", "Nenhuma etapa para exportar.")
            return
        
        try:
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar PDF", "documentacao.pdf", "Arquivos PDF (*.pdf)"
            )
            
            if not output_path:
                return
            
            # Criar PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Página de título
            pdf.add_page()
            pdf.set_font('Arial', 'B', 24)
            pdf.cell(0, 20, self.doc_title, 0, 1, 'C')
            pdf.ln(40)  # Espaço após o título

            # Descrição na capa
            if self.doc_description:
                pdf.set_font('Arial', '', 12)
                description_lines = self.doc_description.split('\n')
                line_height = 8
                total_height = len(description_lines) * line_height
                y_position = (pdf.h - total_height) / 2
                pdf.set_y(y_position)
                
                for line in description_lines:
                    pdf.multi_cell(0, line_height, line, 0, 'C')

            # Configurações de layout
            page_margin = 15
            content_width = pdf.w - (2 * page_margin)
            
            # Processar cada etapa
            for i, step in enumerate(self.steps, 1):
                pdf.add_page()
                current_y = page_margin
                
                # Título da etapa
                pdf.set_font('Arial', 'B', 14)
                pdf.set_xy(page_margin, current_y)
                pdf.cell(content_width, 10, f'Etapa {i}', 0, 1, 'L')
                current_y += 15
                
                # Descrição
                if step.description.strip():
                    pdf.set_font('Arial', '', 11)
                    pdf.set_xy(page_margin, current_y)
                    pdf.multi_cell(content_width, 5, 
                                 step.description.encode('latin-1', 'replace').decode('latin-1'))
                    current_y = pdf.get_y() + 10
                
                # Imagem
                if os.path.exists(step.image_path):
                    try:
                        # Obter dimensões originais da imagem
                        img = Image.open(step.image_path)
                        img_w, img_h = img.size
                        
                        # Calcular espaço disponível para a imagem
                        available_height = pdf.h - current_y - (2 * page_margin)
                        max_image_height = min(180, available_height)  # Limitar altura máxima
                        
                        # Calcular escala mantendo proporção
                        scale = min(content_width/img_w, max_image_height/img_h)
                        
                        # Se a imagem for muito pequena, não ampliar além de 150%
                        if scale > 1.5:
                            scale = 1.5
                        
                        final_w = img_w * scale
                        final_h = img_h * scale
                        
                        # Centralizar horizontalmente
                        x_centered = page_margin + (content_width - final_w) / 2
                        
                        # Se a imagem não couber na página atual, criar nova página
                        if current_y + final_h > pdf.h - page_margin:
                            pdf.add_page()
                            current_y = page_margin
                        
                        pdf.image(step.image_path, x=x_centered, y=current_y, 
                                w=final_w, h=final_h)
                        
                    except Exception as e:
                        pdf.set_font('Arial', 'I', 10)
                        pdf.cell(0, 10, f'Erro ao carregar imagem: {str(e)}', 0, 1, 'L')
        
            # Salvar PDF
            pdf.output(output_path)
            
            QMessageBox.information(self, "Sucesso", 
                                  f"PDF gerado com sucesso!\nSalvo em: {output_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {str(e)}")

    def save_template(self):
        if not self.steps:
            QMessageBox.warning(self, "Aviso", "Nenhuma etapa para salvar como template.")
            return
        
        try:
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Template", "template.json", "Arquivos JSON (*.json)"
            )
            
            if not output_path:
                return
            
            import json
            import shutil
            
            template_name = os.path.splitext(os.path.basename(output_path))[0]
            template_dir = os.path.join(os.path.dirname(output_path), template_name)
            os.makedirs(template_dir, exist_ok=True)
            
            template_data = []
            for i, step in enumerate(self.steps):
                step_name = self.step_list.item(i).text()
                
                new_image_name = f"step_{i+1}.png"
                new_image_path = os.path.join(template_dir, new_image_name)
                shutil.copy2(step.image_path, new_image_path)
                
                template_data.append({
                    "name": step_name,
                    "image_path": os.path.join(template_name, new_image_name),
                    "description": step.description
                })
        
            with open(output_path, "w", encoding='utf-8') as json_file:
                json.dump({
                    "template_dir": template_name,
                    "cover": {
                        "title": self.doc_title,
                        "description": self.doc_description
                    },
                    "steps": template_data
                }, json_file, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "Sucesso", 
                      f"Template salvo com sucesso!\nSalvo em: {output_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar template: {str(e)}")

    def load_template(self):
        try:
            # Solicitar arquivo de template
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Carregar Template", "", "Arquivos JSON (*.json)"
            )
            
            if not file_path:
                return
            
            # Carregar dados do template
            import json
            with open(file_path, "r", encoding='utf-8') as json_file:
                template_data = json.load(json_file)
            
            # Carregar dados da capa
            if "cover" in template_data:
                self.doc_title = template_data["cover"].get("title", "Documentação de Processo")
                self.doc_description = template_data["cover"].get("description", "")
            
            template_dir = os.path.dirname(file_path)
            
            # Limpar etapas existentes
            self.steps.clear()
            self.step_list.clear()
            
            # Criar pasta images se não existir
            images_dir = os.path.join(os.path.dirname(__file__), 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            # Adicionar etapas do template
            for i, step_data in enumerate(template_data["steps"]):
                # Caminho da imagem no template
                template_image_path = os.path.join(template_dir, step_data["image_path"])
                
                if os.path.exists(template_image_path):
                    # Copiar imagem para a pasta de desenvolvimento
                    new_image_path = os.path.join(images_dir, f"step_{i+1}.png")
                    import shutil
                    shutil.copy2(template_image_path, new_image_path)
                    
                    step = Step(new_image_path, step_data["description"])
                    self.steps.append(step)
                    
                    item = QListWidgetItem(step_data["name"])
                    self.step_list.addItem(item)
        
            # Selecionar primeira etapa se existir
            if self.step_list.count() > 0:
                self.step_list.setCurrentRow(0)
                self.display_step(self.step_list.item(0))
        
            QMessageBox.information(self, "Sucesso", "Template carregado com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar template: {str(e)}")

    def edit_step_name(self):
        current_item = self.step_list.currentItem()
        if current_item:
            text, ok = QInputDialog.getText(
                self, 
                "Editar Nome", 
                "Digite o novo nome da etapa:",
                QLineEdit.Normal,
                current_item.text()
            )
            if ok and text:
                current_item.setText(text)

    # Adicione este método após init_ui na classe DocCreator
    def edit_cover(self):
        dialog = CoverDialog(self.doc_title, self.doc_description, self)
        if dialog.exec_() == QDialog.Accepted:
            self.doc_title = dialog.title_edit.text()
            self.doc_description = dialog.desc_edit.toPlainText()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar aplicação
    app.setApplicationName("Gerador de Documentação")
    app.setApplicationVersion("1.0")
    
    # Criar e mostrar janela principal
    creator = DocCreator()
    creator.resize(800, 700)
    creator.show()
    
    sys.exit(app.exec_())