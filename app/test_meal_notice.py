import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import Mock
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget
from compact_bubble import CompactBubble
from meal_notice import MealNotice
from meal_reminders import MEAL_MESSAGE

APP=QApplication.instance() or QApplication([])


class MealNoticeTests(unittest.TestCase):
    def setUp(self):
        self.pet=QWidget();self.pet.setFixedSize(180,180);self.pet.settings={'on_top':False}
        self.pet.bubble=CompactBubble();self.pet.bubble.set_mode('mini');self.pet.bubble.size_transition.complete()
        self.pet.start_meal_animation=Mock(return_value=True)
        self.pet.finish_meal_animation=Mock()
        self.pet.acknowledge_meal_reminder=Mock(return_value=True)
        pixmap=QPixmap(180,180);pixmap.fill(Qt.GlobalColor.magenta)
        self.pet.frames=[pixmap];self.pet.draw_frame=lambda painter,rect:painter.drawPixmap(rect.toRect(),pixmap)
        self.pet.show();self.pet.bubble.show();APP.processEvents()
        self.notice=MealNotice(self.pet)

    def tearDown(self):
        self.notice.close();self.notice.deleteLater();self.pet.bubble.close();self.pet.bubble.deleteLater()
        self.pet.close();self.pet.deleteLater();APP.processEvents()

    def test_waits_for_acknowledgement_without_expanding_or_accepting_focus(self):
        size=self.pet.bubble.size();self.notice.present();APP.processEvents()
        self.assertEqual(self.notice.label.text(),MEAL_MESSAGE)
        self.assertTrue(self.notice.active);self.assertTrue(self.notice.timer.isActive())
        self.assertEqual(self.notice.timer.interval(),3000);self.assertFalse(self.notice.timer.isSingleShot())
        self.assertEqual(self.pet.bubble.size(),size);self.assertTrue(self.pet.bubble.is_island())
        self.assertTrue(self.notice.windowHandle().flags() & Qt.WindowType.WindowDoesNotAcceptFocus)
        self.assertFalse(self.notice.windowHandle().flags() & Qt.WindowType.WindowTransparentForInput)
        self.assertFalse(self.notice.windowHandle().flags() & Qt.WindowType.WindowStaysOnTopHint)
        self.notice.copy_once();self.notice.copy_once()
        QTest.mouseClick(self.notice.confirm,Qt.MouseButton.LeftButton);APP.processEvents()
        self.assertFalse(self.notice.active);self.assertFalse(self.notice.timer.isActive())
        self.assertFalse(self.notice.isVisible());self.assertFalse(self.notice.clones.isVisible())
        self.assertEqual(self.notice.clones.count,0);self.assertTrue(self.notice.clones.frame.isNull())
        self.pet.finish_meal_animation.assert_called_once();self.pet.acknowledge_meal_reminder.assert_called_once()
        self.notice.copy_once();self.assertEqual(self.notice.clones.count,0)

    def test_unlimited_count_keeps_one_shared_surface_and_bounded_visible_stacks(self):
        self.notice.present();surface=self.notice.clones;self.notice.copy_once();APP.processEvents()
        slots=len(surface.slots);self.assertGreater(slots,0)
        self.assertTrue(surface.windowHandle().flags() & Qt.WindowType.WindowTransparentForInput)
        surface.count=10**6
        self.notice.copy_once()
        self.assertIs(self.notice.clones,surface);self.assertEqual(surface.count,10**6+1)
        self.assertEqual(len(surface.slots),surface.capacity)
        self.assertIn(str(10**6+2),self.notice.count_label.text())
        self.pet.start_meal_animation.assert_called_once()

    def test_positions_are_random_coordinates_not_grid_cells(self):
        import random
        self.notice.clones.rng=random.Random(123)
        self.notice.present()
        for _ in range(4):self.notice.copy_once()
        surface=self.notice.clones
        self.assertTrue(any(rect.x()%self.pet.width()!=0 for rect in surface.slots))
        self.assertTrue(all(surface.rect().contains(rect) for rect in surface.slots))
        self.assertTrue(all(not rect.intersects(surface.reserved) for rect in surface.slots))

    def test_moving_preserves_reminder_and_hiding_stops_without_acknowledging(self):
        self.notice.present();self.notice.copy_once()
        self.pet.move(self.pet.pos()+QPoint(10,10));APP.processEvents()
        self.assertTrue(self.notice.active);self.assertEqual(self.notice.clones.count,1)
        self.pet.hide();APP.processEvents();APP.processEvents()
        self.assertFalse(self.notice.active);self.assertFalse(self.notice.timer.isActive())
        self.assertFalse(self.notice.clones.isVisible());self.pet.acknowledge_meal_reminder.assert_not_called()
        self.pet.finish_meal_animation.assert_not_called()

    def test_repeated_due_check_does_not_reset_clones_and_failed_ack_stays_actionable(self):
        self.notice.present();self.notice.copy_once();self.notice.present()
        self.assertEqual(self.notice.clones.count,1);self.pet.start_meal_animation.assert_called_once()
        self.pet.acknowledge_meal_reminder.return_value=False
        self.notice.confirm.click();self.assertTrue(self.notice.active);self.assertTrue(self.notice.confirm.isEnabled())
        self.pet.acknowledge_meal_reminder.return_value=True
        self.notice.confirm.click();self.assertFalse(self.notice.active)

    def test_close_and_disabled_style_stop_leave_no_live_copy_timer(self):
        self.notice.present();self.notice.copy_once();self.notice.stop()
        self.assertFalse(self.notice.active);self.assertFalse(self.notice.timer.isActive())
        self.notice.present();self.notice.copy_once();self.notice.close()
        self.assertFalse(self.notice.active);self.assertFalse(self.notice.timer.isActive())
        self.assertFalse(self.notice.clones.isVisible())


if __name__=='__main__':unittest.main()
