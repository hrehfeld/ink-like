from PySide2 import QtCore, QtGui, QtWidgets as W
from PySide2.QtCore import Qt
import sys


class GameWindow(W.QWidget):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)

        self.setWindowTitle("Game")
        layout = W.QHBoxLayout(self)
        layout.setStretch(0, 1)


class ActionsWidget(W.QWidget):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)
        self.setMinimumWidth(200)
        self.setMaximumWidth(500)

    def add_action(self, label, f):
        b = W.QPushButton(label, self)
        b.clicked.connect(f)

class TextWidget(W.QTextEdit):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)
        self.setReadOnly(True)
        #self.setMinimumWidth(200)

    def minimumSizeHint(self):
        return 200

class SizeRespectingScrollArea(W.QScrollArea):
    def minimumSizeHint(self):
        print('minimumSizeHint', self.widget().minimumSizeHint())
        return self.widget().minimumSizeHint()

    def minimumSize(self):
        print('minimumSize', self.widget().minimumSize())
        return self.widget().minimumSize()

    def maximumSize(self):
        return self.widget().minimumSize()

def with_scrollarea(content, parent=None, resizable=False):
    a = SizeRespectingScrollArea(parent)
    a.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    a.horizontalScrollBar().setEnabled(False)
    content.setParent(a)
    a.setWidget(content)
    a.setWidgetResizable(resizable)
    return a


def main():
    app = W.QApplication()

    gamew = GameWindow()

    splitter = W.QSplitter(QtCore.Qt.Horizontal)
    gamew.layout().addWidget(splitter)

    text = TextWidget(gamew)

    splitter.addWidget(with_scrollarea(text, splitter, resizable=True))
    actions = ActionsWidget(gamew)
    splitter.addWidget(actions)

    for i in range(splitter.count()):
        splitter.setCollapsible(i, False)

    for i in range(50):
        text.insertHtml('<b>Rachel:</b> This is an owl.')
        text.append('\n')
    text.insertHtml("<b>Deckard:</b> I'm not here about the owl.")


    actions.add_action('Look Around', lambda *args: print(args))

    gamew.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
