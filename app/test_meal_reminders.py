import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from desktop_core import normalized
from meal_reminders import MealReminders


class MealReminderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'reminders.sqlite3'
        self.reminders = MealReminders(self.path)
        self.settings = normalized({})

    def tearDown(self):
        self.tmp.cleanup()

    def at(self, hour, minute, day=26):
        return datetime(2026, 10, day, hour, minute, 10)

    def test_default_times_once_per_slot_survive_restart_and_repeat_tomorrow(self):
        self.assertFalse(self.reminders.claim(self.settings, self.at(11, 39)))
        self.assertTrue(self.reminders.claim(self.settings, self.at(11, 40)))
        self.reminders = MealReminders(self.path)
        self.assertFalse(self.reminders.claim(self.settings, self.at(11, 40)))
        self.assertTrue(self.reminders.claim(self.settings, self.at(17, 20)))
        self.assertTrue(self.reminders.claim(self.settings, self.at(11, 40, 27)))

    def test_disabled_or_hidden_defers_but_old_missed_reminders_are_not_replayed(self):
        self.assertFalse(self.reminders.claim(dict(self.settings, meal_reminders=False), self.at(11, 40)))
        self.assertFalse(self.reminders.claim(self.settings, self.at(11, 40), available=False))
        self.assertTrue(self.reminders.claim(self.settings, self.at(11, 43)))
        self.assertFalse(self.reminders.claim(self.settings, self.at(17, 25)))

    def test_custom_midnight_and_identical_times_coalesce(self):
        self.settings.update(meal_lunch_time='00:00', meal_dinner_time='00:00')
        self.assertTrue(self.reminders.claim(self.settings, self.at(0, 0)))
        self.assertFalse(self.reminders.claim(self.settings, self.at(0, 1)))
        self.assertFalse(self.reminders.claim(self.settings, self.at(11, 40)))
        self.assertTrue(self.reminders.claim(self.settings, self.at(0, 0, 27)))

    def test_new_time_rearms_slot_but_returning_to_delivered_time_does_not_repeat(self):
        self.assertTrue(self.reminders.claim(self.settings, self.at(11, 40)))
        self.reminders.acknowledge()
        self.settings['meal_lunch_time'] = '11:42'
        self.assertTrue(self.reminders.claim(self.settings, self.at(11, 42)))
        self.reminders.acknowledge()
        self.reminders=MealReminders(self.path)
        self.assertFalse(self.reminders.claim(self.settings,self.at(11,42)))
        self.settings['meal_lunch_time'] = '11:40'
        self.assertFalse(self.reminders.claim(self.settings, self.at(11, 40)))

    def test_idle_ticks_do_not_access_database_and_two_instances_deduplicate(self):
        other = MealReminders(self.path)
        with patch.object(self.reminders, 'connect', side_effect=AssertionError('idle database access')):
            for _ in range(100):
                self.assertFalse(self.reminders.claim(self.settings, self.at(10, 0)))
        self.assertTrue(self.reminders.claim(self.settings, self.at(11, 40)))
        self.assertFalse(other.claim(self.settings, self.at(11, 40)))

    def test_invalid_saved_times_fall_back_without_changing_other_settings(self):
        for value in ('25:00', '12:60', '9:30', '', None, 1140):
            settings = normalized(dict(meal_lunch_time=value, meal_dinner_time=value, sound=False))
            self.assertEqual(settings['meal_lunch_time'], '11:40')
            self.assertEqual(settings['meal_dinner_time'], '17:20')
            self.assertFalse(settings['sound'])

    def test_unacknowledged_reminder_survives_restart_until_confirmed(self):
        self.reminders.claim(self.settings,self.at(11,40))
        restarted=MealReminders(self.path)
        self.assertTrue(restarted.pending)
        restarted.acknowledge()
        self.assertFalse(restarted.pending);self.assertFalse(MealReminders(self.path).pending)
        self.assertFalse(restarted.claim(self.settings,self.at(11,41)))
        self.assertTrue(restarted.claim(self.settings,self.at(17,20)))

    def test_upgrade_does_not_replay_previously_delivered_one_shot_reminders(self):
        import sqlite3
        legacy=Path(self.tmp.name)/'legacy.sqlite3'
        with sqlite3.connect(legacy) as db:
            db.execute('CREATE TABLE delivered(day TEXT,slot TEXT,PRIMARY KEY(day,slot))')
            db.execute("INSERT INTO delivered VALUES('2026-10-26','meal_lunch_time')")
        reminder=MealReminders(legacy)
        self.assertFalse(reminder.pending)
        self.assertFalse(reminder.claim(self.settings,self.at(12,0)))
        self.settings['meal_lunch_time']='20:57'
        self.assertTrue(reminder.claim(self.settings,self.at(20,57)))

    def test_legacy_pending_migrates_once_and_ack_survives_restart(self):
        import sqlite3
        legacy=Path(self.tmp.name)/'pending.sqlite3'
        with sqlite3.connect(legacy) as db:
            db.execute('CREATE TABLE delivered(day TEXT,slot TEXT,acknowledged INTEGER,PRIMARY KEY(day,slot))')
            db.execute("INSERT INTO delivered VALUES('2026-10-26','meal_dinner_time',0)")
        reminder=MealReminders(legacy);self.assertTrue(reminder.pending)
        reminder.acknowledge();self.assertFalse(MealReminders(legacy).pending)


if __name__ == '__main__':
    unittest.main()
