from PySide2 import QtCore, QtGui, QtWidgets as W
from PySide2.QtCore import Qt
import sys
import collections
import time
import random

QSizePolicy = W.QSizePolicy


def children_widgets(w):
    l = w.layout()
    for i in range(l.count()):
        item_widget = l.itemAt(i).widget()

        if item_widget:
            yield item_widget
    

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


class SizeRespectingScrollArea(W.QScrollArea):
    def minimumSizeHint(self):
        return self.widget().minimumSizeHint()

    def minimumSize(self):
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


class ActionsWidget(W.QWidget):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)

        l = W.QVBoxLayout()

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


    def minimumSize(self):
        return self.content.minimumSize()

    def minimumSizeHint(self):
        return self.content.minimumSizeHint()

    def set_actions(self, actions):
        l = self.content.layout()
        while l.count():
            item_widget = l.takeAt(0).widget()
            
            # need to unset parent!
            # not all items are widgets
            if item_widget:
                item_widget.setParent(None)

        topics = dict(sorted([(topic, None) for topic, label, f in actions]))
        if 1:
            for topic in topics:
                print('adding topic', topic)
                g = W.QGroupBox(topic)
                g.setLayout(FlowLayout())
                #g.setLayout(W.QVBoxLayout())
                l = self.content.layout()
                l.addWidget(g)
                topics[topic] = g.layout()

        for topic, label, f in actions:
            b = W.QPushButton(label, self)
            b.clicked.connect(f)
            #l.addWidget(b)
            topics[topic].addWidget(b)

        l.addStretch(1)

    def setEnabled(self, enabled):
        for group in children_widgets(self.content):
            for button in children_widgets(group):
                if isinstance(button, W.QPushButton):
                    button.setEnabled(enabled)
                


class TextWidget(W.QTextEdit):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)
        self.setReadOnly(True)

    def minimumSizeHint(self):
        return QtCore.QSize(200, 200)


class GameWindow(W.QWidget):
    def __init__(self, parent=None):
        super(type(self), self).__init__(parent)
        self.setWindowTitle("Ink-like")

        text = TextWidget()
        self.text = text
        actions = ActionsWidget()
        self.actions = actions

        splitter = W.QSplitter(QtCore.Qt.Horizontal)

        splitter.addWidget(text)
        splitter.addWidget(actions)
        for i in range(splitter.count()):
            splitter.setCollapsible(i, False)
        splitter.setSizes([10, 300])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        

        layout = W.QHBoxLayout(self)
        layout.addWidget(splitter)
        layout.setStretch(0, 1)

        self.setLayout(layout)
        
    def add_paragraph(self, text):
        self.text.insertHtml(text)
        self.text.append('\n')
        self.text.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def say(self, name, text, color='#000'):
        self.add_paragraph('<b style="color: {color}">{name}:</b> {text}'.format(name=name, text=text, color=color))
        
    def describe(self, text, color='#000'):
        self.add_paragraph('<span style="color: %s">' % color + text + '</span>')

    def act(self, text, color='#000'):
        self.add_paragraph('<i style="color: {color}">{text}</i>'.format(text=text, color=color))

    def set_actions(self, actions):
        self.actions.set_actions(actions)

    def setEnabled(self, enabled):
        return self.actions.setEnabled(enabled)
        
    
class State:
    def __init__(self):
        self.state = collections.defaultdict(State)

    def __getattr__(self, k):
        #if k == 'state':
        #    return super(type(self), self).__getattr__(k)
        return self.state[k]

    def __setattr__(self, k, v):
        if k == 'state':
            super(type(self), self).__setattr__(k, v)
        else:
            self.state[k] = v

    def __contains__(self, k):
        return k in self.state
    

EPSILON = 0.0001

def main():
    app = W.QApplication()

    gamew = GameWindow()
    gamew.show()

    describe = gamew.describe
    say = gamew.say
    act = gamew.act
    def delay():
        gamew.setEnabled(False)
        gamew.repaint()
        time.sleep(0.5)
        gamew.setEnabled(True)

    LOCATION_HALL = 0

    def at_location(location):
        return state.location == location

    state = State()
    state.time = 0
    actions = []

    def loop():
        action_buttons = []

        # messages first
        for predicate, labels, action in actions:
            if labels is None and predicate():
                delay()
                action()

        # then generate action list
        for predicate, labels, action in actions:
            if labels is not None and predicate():
                action_buttons.append((*labels(), action))

        gamew.set_actions(action_buttons)
        state.time += 1

    def duration(since_time):
        return state.time - since_time



    state.location = LOCATION_HALL
    state.location_enter_time = 0
    state.actors = {LOCATION_HALL: []}

    def actor_is_present(actor):
        return actor in state.actors[state.location]

    def actor_make_present(actor):
        state.actors[state.location].append(actor)

    class Actor:
        def __init__(self, name, color):
            self.name = name
            self.color = color

        def act(self, text):
            act(text, self.color)

        def say(self, text):
            say(self.name, text, self.color)

        def is_present(self):
            return actor_is_present(self)

        def enter(self):
            return actor_make_present(self)

    actor_self = Actor('Deckard', '#444')
    actor_owl = Actor('Owl', '#740')
    #actor_rachel = Actor('Rachel', '#900')


    def location_duration():
        return duration(state.location_enter_time)

    def maybe(p=0.5):
        return p > random.uniform(0, 1)

    def at_first(loc, p=0.5, factor=0.9, min=0):
        if 'act' in loc:
            return loc.act()
        def act():
            nonlocal p
            print('using at first', p)
            r = maybe(p)
            p *= factor
            if p < min:
                p = min
            return r
        print('adding at first')
        loc.act = act
        

    def wait():
        actor_self.act("You slowly let your eyes wander around the room.")
        loop()
    actions.append(((lambda: True), lambda: ('World', 'Wait'), wait))

    class Hall:
        @staticmethod
        def look_around():
            describe("The hall is vast and largely empty. At the far end there's a desk.")
            state.hall.seen = True
            loop()

        class Desk:
            @staticmethod
            def describe_desk():
                if not state.hall.desk.seen:
                    actor_self.act("Carefully, you approach the desk.")
                    delay()
                describe("The desk is surprisingly large and made of shiny, expensive wood. Somehow, you're afraid to touch it.")
                describe("A strange metal thing is standing on the desk, which you can only describe as a mixture between a candle holder and a weird sculpture.")
                state.hall.desk.seen = True
                loop()

    def inside_hall():
        return at_location(LOCATION_HALL)

    state.hall.seen = False
    state.hall.desk.seen = False
    actions.append(((lambda: inside_hall() and not state.hall.seen), lambda: ('World', 'Look Around'), Hall.look_around))
    actions.append(((lambda: inside_hall() and state.hall.seen),
                    lambda: ('World', 'Take a look at the desk' if not state.hall.desk.seen else 'Take another look at the desk'),
                    Hall.Desk.describe_desk))

    def hall_owl_intro():
        actor_owl.act("Suddenly, you hear a flapping noise from the dark!")
        actor_owl.act("You quickly turn around, just in time to see an owl fly towards you. You freeze for a moment, wondering how to defend against a wild animal.")
        delay()
        actor_owl.act("You can't suppress a relieved sigh as the owl dashes past you and lands on the strange object on the desk, which turns out to be an owl seat.")
        actor_make_present(actor_owl)
    actions.append(((lambda: inside_hall() and location_duration() > 2 and state.hall.desk.seen and not actor_owl.is_present() and maybe(0.45)), None, hall_owl_intro))

    state.owl.look.last = 0
    def hall_owl_look():
        if inside_hall():
            actor_owl.act("The owl looks at you, somehow questioning your presence here.")
        else:
            actor_owl.act("The owl looks at you sceptically.")
        state.owl.look.last = state.time
    actions.append(((lambda: actor_owl.is_present() and at_first(state.owl.look, min=0.1) and duration(state.owl.look.last) > 0, None, hall_owl_look)))
    
    def hall_owl_inspect():
        actor_self.act("Trying not to disturb the owl, you take a look at it. It is an owl of impressive size, with large, round eyes, brown and white feathers. It sits on the metal bar you saw on the desk earlier.")
        actor_owl.act("The owl stares back at you, undisturbed by your inspection.")
        state.owl.look.last = state.time
        loop()
    actions.append(((lambda: actor_owl.is_present(), lambda: ('World', 'Take a peek at the owl.'), hall_owl_inspect)))


    # END world
    
    loop()

    #     for i in range(50):
    #     gamew.say('Rachel', 'This is an owl.')
    # gamew.say('Deckard', "I'm not here about the owl.")


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
