from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLayout
from PyQt5.QtWidgets import   QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat,QTextBlockFormat, QFont,   QPixmap, QTextBlock,QTextCursor
from PyQt5.QtCore import Qt, QSize,QTimer
  
import sys
from dotenv import dotenv_values
import os

env_vars = dotenv_values(os.path.join(os.path.dirname(os.path.dirname(__file__)),"Backend", ".env"))



Assistantname= env_vars.get("Assistantname")

current_dir = os.path.dirname(os.path.abspath(__file__))
old_chat_message = ""
TempDirPath = rf"{current_dir}\Files"
GraphicsDirPath = rf"{current_dir}\Graphics"

def answerModifier(answer):
    lines = answer.split('\n')          # split the response into lines
    non_empty_lines = [line for line in lines if line.strip()]      # removes empty lines
    modified_answer = '\n'.join(non_empty_lines)            # joins cleaned lines back together
    return modified_answer


def QueryModifier(Query):
    new_query = Query.strip().lower()

    # Remove trailing punctuation for clean check
    if new_query and new_query[-1] in ".!?":
        new_query = new_query[:-1]

    # Check if it starts with a known question phrase
    question_words = [
        "how", "what", "when", "who", "where", "can you", "could you", "will you",
        "would you", "why", "is you", "are you", "whom", "whose", "was it", "was you"
    ]

    is_question = any(new_query.startswith(q) for q in question_words)

    # Add proper punctuation
    if is_question:
        new_query += "?"
    else:
        new_query += "."

    return new_query.capitalize()

def setMicrophoneStatus(Command):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf"{TempDirPath}\Mic.data", "w", encoding='utf-8') as file:
        file.write(Command)

def getMicrophoneStatus():
     os.makedirs(TempDirPath, exist_ok=True)
     with open(rf"{TempDirPath}\Mic.data", "r", encoding='utf-8') as file:
         Status = file.read()
     return Status

def setAssistantStatus(Status):
     os.makedirs(TempDirPath, exist_ok=True)  # ✅ ensure path exists
     with open(rf"{TempDirPath}\Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def getAssistantStatus():
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf"{TempDirPath}\Status.data", "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def micButtonInitialized():
    setMicrophoneStatus("False")

def minButtonClosed():
    setMicrophoneStatus("True")

def graphicsDirectoryPath(Filename):
    path = rf"{GraphicsDirPath}\{Filename}"
    return path

def tempDirectoryPath(Filename):
    path = rf"{TempDirPath}\{Filename}"
    return path

def showTextToScreen(Text):
    with open(rf"{TempDirPath}\Responses.data", 'w', encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(10)
        self.chat_text_edit= QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        layout.setStretch(0,1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text= QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(graphicsDirectoryPath('jarvis.gif'))
        max_gif_size_W = 100
        max_gif_size_H = 100
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        self.label= QLabel("")
        self.label.setStyleSheet("color: White; font-size:16px; margin-right: 195 px; border: none;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(10)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(500)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet(""" 
                           
             QWidget {
                  background-color: black;
            }
            QScrollBar: vertical{
                border:none;
                background: black;
                width:10px;
                margin: 0px;
                }
                           
            QScrollBar::handle:vertical{
                background:white;
                min-height: 20px;               
                 }
                           
            QScrollBar::add-line:vertical{
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
                }
            
            QScrollBar::sub-line:vertical{
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;      
                }
                           
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{
                border: none;
                background: none;
                width: 0px;
                height: 0px;           
                }
                           
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
                 background: none;           
                }
            
                """)
        
    def loadMessages(self):
        global old_chat_message

        with open(tempDirectoryPath('Responses.data'), "r", encoding= 'utf-8') as file:
            messages= file.read()

            if None == messages:
                pass
            elif len(messages)<=1:
                pass
            elif str(old_chat_message)==str(messages):
                pass
            else:
                self.addMessage(message=messages, color= 'white')
                old_chat_message= messages
    
    def SpeechRecogText(self):
        with open(tempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height= 60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event= None):
        if self.toggled:
            self.load_icon(graphicsDirectoryPath('mic_off.jpg'), 60,60)
            micButtonInitialized()
        else:
            self.load_icon(graphicsDirectoryPath('mic_on.png'), 60, 60)
            minButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format= QTextCharFormat()
        formatm= QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)
        desktop= QApplication.desktop()
        screen_width= desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout= QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        gif_label = QLabel()
        movie = QMovie(graphicsDirectoryPath('jarvis.gif'))
        gif_label.setMovie(movie)
        # Reduce GIF to fixed size (e.g., 300x168)
        scaled_width = 900
        scaled_height = int(scaled_width / 12 * 9)
        movie.setScaledSize(QSize(scaled_width, scaled_height))

        # Don't allow it to expand to full screen
        gif_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        gif_label.setAlignment(Qt.AlignCenter)

        movie.start()
        self.icon_label = QLabel()
        pixmap = QPixmap(graphicsDirectoryPath('mic_off.jpg'))
        new_pixmap =pixmap.scaled(60,60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled= True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("")
        self.label.setStyleSheet("color: White; font-size=16px; margin-bottom:0;")
        content_layout.addWidget(gif_label, alignment= Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment= Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment= Qt.AlignCenter)
        content_layout.setContentsMargins(0,0,0,150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(tempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height= 60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event= None):
        if self.toggled:
            self.load_icon(graphicsDirectoryPath('mic_off.jpg'), 60,60)
            micButtonInitialized()
        else:
            self.load_icon(graphicsDirectoryPath('mic_on.png'), 60, 60)
            minButtonClosed()

        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)
        desktop= QApplication.desktop()
        screen_width= desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label =QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class customTopBar(QWidget):

    def __init__(self,parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()
        self.current_screen = None
        

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon = QIcon(graphicsDirectoryPath("home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home ")
        home_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        message_button = QPushButton()
        message_icon = QIcon(graphicsDirectoryPath("chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat ")
        message_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        minimize_button = QPushButton()
        minimize_icon = QIcon(graphicsDirectoryPath("minimize2.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color: white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(graphicsDirectoryPath("maximize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color: white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        
        self.restore_icon = QIcon(graphicsDirectoryPath("minimize.png"))

        close_button = QPushButton()
        close_icon = QIcon(graphicsDirectoryPath("close.png"))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color: white")
        close_button.clicked.connect(self.parent().close)

        line_frame =QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")

        title_label = QLabel(f" Jarvis.ai  ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)
    
    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset= event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)
       
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        initial_screen = InitialScreen(self)
        layout =self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width= desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0,0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = customTopBar(self,stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app= QApplication(sys.argv)
    window= MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()











        





    







                









