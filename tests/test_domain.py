import unittest
from copy import deepcopy
from medical_prescription.domain import build_grid, duplication_outcome, frequency_interval, period_days, spacing_allowed


class DomainTests(unittest.TestCase):
    def item(self, **changes):
        return dict(item_unique_key='order-a',medication='Synthetic Medication',frequency='BID',
                    period='2 Days',allow_duplicate_next_day=1,**changes)

    def test_distinct_orders_of_same_medication_do_not_merge(self):
        first=self.item()
        second={**first,'item_unique_key':'order-b'}
        rows=build_grid([first,second],[],'2026-11-04')
        self.assertEqual(len(rows),48)
        self.assertEqual(len({r['schedule_unique_key'] for r in rows}),48)

    def test_rebuild_is_idempotent_and_retains_completed_history(self):
        rows=build_grid([self.item()],[],'2026-11-04')
        rows[0].update(completed=1,given_by='synthetic-nurse',given_on='2026-11-04 10:03:00')
        original=deepcopy(rows)
        self.assertEqual(build_grid([self.item()],rows,'2026-11-04'),original)
        self.assertEqual(build_grid([],rows,'2026-11-04'),original)
        self.assertEqual(rows,original)

    def test_ambiguous_legacy_keys_rejected(self):
        with self.assertRaises(ValueError):
            build_grid([self.item()],[{'medication':'Synthetic Medication'}],'2026-11-04')
        with self.assertRaises(ValueError):
            build_grid([self.item(),self.item()],[],'2026-11-04')

    def test_hold_rows_retained_but_stopped_new_rows_not_generated(self):
        self.assertEqual(len(build_grid([self.item(hold=1)],[],'2026-11-04')),24)
        self.assertEqual(build_grid([self.item(is_stopped=1)],[],'2026-11-04'),[])

    def test_pending_phone_order_has_no_schedule(self):
        self.assertEqual(build_grid([self.item(is_phone_order=1)],[],'2026-11-04'),[])

    def test_nursing_day_and_overnight_spacing(self):
        rows=build_grid([self.item()],[],'2026-11-04')
        self.assertEqual(rows[0]['scheduled_time'],'10:00:00')
        self.assertEqual(rows[-1]['scheduled_time'],'09:00:00')
        self.assertFalse(spacing_allowed('23:00:00','01:00:00',4))
        self.assertTrue(spacing_allowed('22:00:00','02:00:00',4))
        self.assertEqual(frequency_interval('q48h'),48)

    def test_period_and_duplication_match_source(self):
        self.assertEqual(period_days('2 Weeks'),14)
        self.assertEqual(period_days('unknown'),0)
        self.assertEqual(duplication_outcome(self.item(),True),(None,1))
        self.assertEqual(duplication_outcome(self.item(),False),(None,2))
        self.assertEqual(duplication_outcome({**self.item(),'frequency':'STAT'},False),('One-Time Completed',0))
        self.assertEqual(duplication_outcome(self.item(is_stopped=1),False),('Stopped',0))
        self.assertEqual(duplication_outcome({**self.item(),'period':'1 Day'},True),('Course Completed',0))


if __name__=='__main__':
    unittest.main()

