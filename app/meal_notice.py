"""Acknowledged meal reminder with one shared, click-through clone surface."""
from PySide6.QtCore import Qt, QTimer, QEvent, QPoint, QRect, QRectF
from PySide6.QtGui import QColor, QPainter, QPixmap, QRegion
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from typography import ui_font
from ui_theme import SURFACE, INK, BORDER, PRIMARY, ON_PRIMARY
from meal_reminders import MEAL_MESSAGE


def passive_flags(on_top, click_through=False):
    flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowDoesNotAcceptFocus
    if on_top:
        flags |= Qt.WindowType.WindowStaysOnTopHint
    if click_through:
        flags |= Qt.WindowType.WindowTransparentForInput
    return flags


def passive_attributes(widget):
    widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
    widget.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
    widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class MealClones(QWidget):
    """Draw visible stacks once; logical copy count has no limit.

    Identical, synchronized sprites at the same position occlude each other.
    After filling the screen we stack there, rather than allocating another
    native window, decoder, pixmap or rectangle for every logical copy.
    """
    def __init__(self, pet, notice):
        super().__init__(None, passive_flags(pet.settings.get('on_top', True), True))
        passive_attributes(self)
        self.pet = pet
        self.notice = notice
        self.count = 0
        self.slots = []
        self.frame = QPixmap()
        self.region = QRegion()
        self.setWindowTitle('妮可吃饭提醒分身')

    def arrange(self):
        screen = QApplication.screenAt(self.pet.frameGeometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.setGeometry(area)
        w, h = min(self.pet.width(), area.width()), min(self.pet.height(), area.height())
        origin = self.pet.frameGeometry().translated(-area.topLeft())
        reserved = self.notice.frameGeometry().translated(-area.topLeft())
        candidates = [QRect(x, y, w, h)
                      for y in range(max(0, area.height() - h), -1, -max(1, h))
                      for x in range(0, max(1, area.width() - w + 1), max(1, w))]
        candidates.sort(key=lambda rect: (rect.center() - origin.center()).manhattanLength())
        self.slots = [rect for rect in candidates if not rect.intersects(origin) and not rect.intersects(reserved)]
        if not self.slots:
            # Tiny screens may need overlapping pets, but keep the button clear.
            self.slots = sorted(candidates,key=lambda rect:rect.intersected(reserved).width()*rect.intersected(reserved).height())[:1]
        self.refresh_region()

    def refresh_region(self):
        self.region = QRegion()
        for rect in self.slots[:min(self.count, len(self.slots))]:
            self.region |= QRegion(rect)
        self.update()

    def copy_once(self):
        self.count += 1
        self.refresh_region()
        if not self.isVisible():
            self.show()

    def refresh_frame(self):
        if not self.count or not self.pet.frames:
            return
        # Render the original sprite just once, including its scale/offset.
        ratio=self.devicePixelRatioF()
        frame = QPixmap(round(self.pet.width()*ratio),round(self.pet.height()*ratio))
        frame.setDevicePixelRatio(ratio)
        frame.fill(Qt.GlobalColor.transparent)
        painter = QPainter(frame)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.pet.draw_frame(painter, QRectF(0,0,self.pet.width(),self.pet.height()))
        painter.end()
        self.frame = frame
        self.update(self.region)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(event.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self.frame.isNull():
            return
        for rect in self.slots[:min(self.count, len(self.slots))]:
            if event.region().intersects(rect):
                painter.drawPixmap(rect, self.frame)

    def clear(self):
        self.hide()
        self.count = 0
        self.slots.clear()
        self.region = QRegion()
        self.frame = QPixmap()


class MealNotice(QWidget):
    def __init__(self, pet):
        super().__init__(None, passive_flags(pet.settings.get('on_top', True)))
        passive_attributes(self)
        self.pet = pet
        self.active = False
        self.clones = MealClones(pet,self)
        self.destroyed.connect(self.clones.deleteLater)
        self.setWindowTitle('妮可提醒主人吃饭')
        self.setFixedWidth(300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        self.label = QLabel(MEAL_MESSAGE)
        self.label.setFont(ui_font(16));self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label = QLabel()
        self.count_label.setFont(ui_font(12));self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.confirm = QPushButton('我知道了～')
        self.confirm.setObjectName('acknowledge_meal')
        self.confirm.setFont(ui_font(14));self.confirm.setMinimumHeight(36)
        self.confirm.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.confirm.clicked.connect(self.acknowledge)
        self.setStyleSheet(f'QLabel{{color:{INK};background:transparent;}} QPushButton{{background:{PRIMARY};color:{ON_PRIMARY};border:0;border-radius:8px;padding:6px 12px;}}')
        for widget in (self.label, self.count_label, self.confirm):
            layout.addWidget(widget)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.copy_once)
        pet.installEventFilter(self)
        pet.bubble.installEventFilter(self)
        QApplication.instance().screenRemoved.connect(self.screen_changed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(SURFACE));painter.setPen(QColor(BORDER))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

    def present(self):
        if self.active:
            return
        self.active = True
        self.label.setText(MEAL_MESSAGE)
        self.update_count()
        self.reposition()
        self.clones.arrange()
        if not self.pet.start_meal_animation():
            self.active = False
            self.label.setText(MEAL_MESSAGE + '\nhungry 动作暂不可用，请检查角色素材。')
        else:
            self.timer.start()
        self.update_count()
        self.reposition()
        self.show()  # No activateWindow(), raise_(), panel navigation or sound.

    def sync_flags(self):
        for widget,through in ((self,False),(self.clones,True)):
            visible=widget.isVisible()
            widget.setWindowFlags(passive_flags(self.pet.settings.get('on_top',True),through))
            if visible:widget.show()

    def update_count(self):
        self.count_label.setText(f'妮可 × {self.clones.count + 1}，每 5 秒增加一个分身')

    def reposition(self):
        anchor = self.pet.bubble if self.pet.bubble.isVisible() else self.pet
        rect = anchor.frameGeometry()
        screen = QApplication.screenAt(rect.center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.adjustSize()
        x = max(area.left(), min(rect.center().x() - self.width() // 2, area.right() - self.width() + 1))
        y = rect.top() - self.height() - 8
        if y < area.top():
            y = rect.bottom() + 8
        y = max(area.top(), min(y, area.bottom() - self.height() + 1))
        self.move(QPoint(x, y))

    def copy_once(self):
        if not self.active:
            return
        self.clones.copy_once()
        self.clones.refresh_frame()
        self.update_count()

    def acknowledge(self):
        if self.pet.acknowledge_meal_reminder():
            self.stop()
        else:
            self.label.setText('确认暂未保存，请再点一次「我知道了～」。')

    def stop(self, restore=True):
        was_active = self.active
        self.active = False
        self.timer.stop()
        self.clones.clear()
        self.hide()
        if was_active and restore:
            self.pet.finish_meal_animation()

    def check_visibility(self):
        if not self.pet.isVisible() and self.active:
            self.stop(restore=False)

    def screen_changed(self, *args):
        if self.active:
            self.reposition();self.clones.arrange()

    def eventFilter(self, watched, event):
        if self.active:
            if event.type() == QEvent.Type.Hide and watched is self.pet:
                QTimer.singleShot(0, self, self.check_visibility)
            elif event.type() in (QEvent.Type.Move, QEvent.Type.Resize):
                self.reposition();self.clones.arrange()
        return False

    def closeEvent(self, event):
        self.stop(restore=False)
        self.clones.close()
        super().closeEvent(event)
