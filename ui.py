from PySide2 import QtCore, QtGui, QtWidgets as W
from PySide2.QtCore import Qt
import sys
import collections

QSizePolicy = W.QSizePolicy


class GameWindow(W.QWidget):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)

        self.setWindowTitle("Game")
        layout = W.QHBoxLayout(self)
        layout.setStretch(0, 1)


class FlowLayout(W.QLayout):
    def __init__(self):
        super(type(self), self).__init__()

        self.children = []

        #self.setLayout(W.QVBoxLayout())
        #self.content.layout().inse

    def count(self):
        return len(self.children)

    def itemAt(self, i):
        if i >= self.count():
            return None
        return self.children[i]

    def takeAt(self, i):
        if i >= self.count():
            return None
        return self.children.pop(i)

    def addItem(self, item):
        self.children.append(item)

    def setGeometry(self, rect):
        super(type(self), self).setGeometry(rect)

        self.process_layout(rect, True)

    def process_layout(self, rect, apply_layout):
        padding = self.getContentsMargins()
        rect = rect.adjusted(*padding)

        x = 0
        y = 0
        row_height = 0
        for item in self.children:
            margin_x = self.smart_spacing(W.QStyle.PM_LayoutHorizontalSpacing)
            margin_y = self.smart_spacing(W.QStyle.PM_LayoutVerticalSpacing)

            item_style = item.widget().style()
            if margin_x == -1:
                margin_x = item_style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
                margin_y = item_style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            item_size = item.sizeHint()

            x_end = x + item_size.width()
            # only break after the first widget per row
            if x_end > rect.width() and row_height > 0:
                x = 0
                y += row_height + margin_y
                row_height = 0
            if apply_layout:
                geom = QtCore.QRect(rect.x() + x, rect.y() + y, item_size.width(), item_size.height())
                item.setGeometry(geom)
            x += item_size.width() + margin_x
            row_height = max(row_height, item_size.height())
        return y + row_height + padding[2] + padding[3]
        

    def expandingDirections(self):
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, w):
        h = self.process_layout(QtCore.QRect(0, 0, w, 0), False)
        #print(w, h)
        return h

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        min_w = 0
        min_h = 0
        for item in self.children:
            item_size = item.minimumSize()
            min_w = max(min_w, item_size.width())
            min_h = max(min_h, item_size.height())
        padding = self.getContentsMargins()
        size = QtCore.QSize(min_w + padding[2] + padding[3], min_h)
        print('minimum size', size)
        return size


    def smart_spacing(self, pixel_metric):
        parent = self.parent()
        if parent is None:
            return -1
        if parent.isWidgetType():
            return parent.style().pixelMetric(pixel_metric, None, parent)
        return parent.spacing()
    

class ActionsWidget(W.QWidget):
    NUM_COLS = 4
    COL_WIDTH = 50

    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)

        l = W.QVBoxLayout()
        l.addStretch(1)

        content = W.QWidget()
        content.setLayout(l)
        self.content = content


        a = SizeRespectingScrollArea(parent)
        a.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        a.horizontalScrollBar().setEnabled(False)
        a.setWidgetResizable(True)
        a.setWidget(content)

        l = W.QVBoxLayout()
        l.addWidget(a)

        self.setLayout(l)

        self.topics = {}


    def add_action(self, topic, label, f):
        b = W.QPushButton(label, self)
        b.clicked.connect(f)

        if not topic in self.topics:
            g = W.QGroupBox(topic)
            g.setLayout(FlowLayout())
            l = self.content.layout()
            l.insertWidget(l.count() - 1, g)
            self.topics[topic] = g

        l = self.topics[topic].layout()
        n = l.count()
        l.addWidget(b)#, int(n / self.NUM_COLS), n % self.NUM_COLS)

    def minimumSize(self):
        print(self.content.minimumSize())
        return self.content.minimumSize()

    def minimumSizeHint(self):
        print(self.content.minimumSizeHint())
        return self.content.minimumSizeHint()

class TextWidget(W.QTextEdit):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)
        self.setReadOnly(True)

    def minimumSizeHint(self):
        return QtCore.QSize(200, 200)

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
    a.setWidgetResizable(resizable)
    a.setWidget(content)
    return a


def main():
    app = W.QApplication()

    gamew = GameWindow()

    splitter = W.QSplitter(QtCore.Qt.Horizontal)
    gamew.layout().addWidget(splitter)

    text = TextWidget()

    splitter.addWidget(text)
    actions = ActionsWidget()
    splitter.addWidget(actions)
    #splitter.addWidget(actions)

    for i in range(splitter.count()):
        splitter.setCollapsible(i, False)
    splitter.setSizes([10, 300])
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 0)

    for i in range(50):
        text.insertHtml('<b>Rachel:</b> This is an owl.')
        text.append('\n')
    text.insertHtml("<b>Deckard:</b> I'm not here about the owl.")


    for i in range(7):
        actions.add_action('World', 'Look Around' + str(i), lambda *args: print(args))
    for i in range(4):
        actions.add_action('People', 'Talk to' + str(i), lambda *args: print(args))

    gamew.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
