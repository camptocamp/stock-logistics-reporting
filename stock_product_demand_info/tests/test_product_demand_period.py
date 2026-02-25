# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo.exceptions import UserError

from .common import StockProductDemandInfoCommon


class TestProductDemandPeriod(StockProductDemandInfoCommon):
    def test_validation_invalid_expression_create(self):
        with self.assertRaisesRegex(UserError, "Invalid date expression"):
            self.env["product.demand.period"].create(
                {
                    "name": "Bad",
                    "start_expression": "invalid-expression",
                    "end_expression": "today",
                }
            )

    def test_validation_invalid_expression_write(self):
        period = self.env["product.demand.period"].create(
            {
                "name": "Good",
                "start_expression": "today -7d",
                "end_expression": "today",
            }
        )
        with self.assertRaisesRegex(UserError, "Invalid date expression"):
            period.write({"start_expression": "bad"})

    def test_validation_start_after_end(self):
        with self.assertRaisesRegex(
            UserError, "Start expression must be before or equal to end"
        ):
            self.env["product.demand.period"].create(
                {
                    "name": "Reversed",
                    "start_expression": "today",
                    "end_expression": "today -7d",
                }
            )

    def test_demand_product_no_warehouse(self):
        """Product demand_period_info aggregates outgoing moves when no warehouse."""
        self.period_7d.active = True
        self._create_outgoing_move(self.product, self.today - timedelta(days=3), 10.0)
        self._create_outgoing_move(self.product, self.today - timedelta(days=1), 5.0)
        self.product.invalidate_recordset(["demand_period_info"])
        key = str(self.period_7d.id)
        self.assertTrue(self.product.demand_period_info)
        self.assertIn(key, self.product.demand_period_info)
        self.assertEqual(self.product.demand_period_info[key]["value"], 15.0)
        self.assertEqual(self.product.demand_period_info[key]["name"], "Last 7 days")
        self.assertIn("sequence", self.product.demand_period_info[key])

    def test_demand_orderpoint_warehouse(self):
        """Orderpoint demand_period_info is warehouse-scoped."""
        self.period_7d.active = True
        self._create_outgoing_move(self.product, self.today - timedelta(days=2), 7.0)
        self.orderpoint.invalidate_recordset(["demand_period_info"])
        key = str(self.period_7d.id)
        self.assertTrue(self.orderpoint.demand_period_info)
        self.assertIn(key, self.orderpoint.demand_period_info)
        self.assertEqual(self.orderpoint.demand_period_info[key]["value"], 7.0)
        self.assertEqual(self.orderpoint.demand_period_info[key]["name"], "Last 7 days")

    def test_demand_no_active_periods(self):
        """With no active periods, demand_period_info is empty."""
        self.product.invalidate_recordset(["demand_period_info"])
        self.assertFalse(self.product.demand_period_info)

    def test_demand_period_no_moves_in_range(self):
        """Period with no moves in range yields zero for that period."""
        self.period_7d.active = True
        self.product.invalidate_recordset(["demand_period_info"])
        key = str(self.period_7d.id)
        self.assertTrue(self.product.demand_period_info)
        self.assertIn(key, self.product.demand_period_info)
        self.assertEqual(self.product.demand_period_info[key]["value"], 0.0)
        self.assertEqual(self.product.demand_period_info[key]["name"], "Last 7 days")

    def test_demand_template_sum_of_variants(self):
        """product.template demand_period_info is the sum of its variants' demand."""
        self.period_7d.active = True
        self._create_outgoing_move(self.variant_s, self.today - timedelta(days=2), 10.0)
        self._create_outgoing_move(self.variant_m, self.today - timedelta(days=1), 5.0)
        self.template_with_variants.invalidate_recordset(["demand_period_info"])
        self.variant_s.invalidate_recordset(["demand_period_info"])
        self.variant_m.invalidate_recordset(["demand_period_info"])
        key = str(self.period_7d.id)
        self.assertEqual(self.variant_s.demand_period_info[key]["value"], 10.0)
        self.assertEqual(self.variant_m.demand_period_info[key]["value"], 5.0)
        self.assertIn(key, self.template_with_variants.demand_period_info)
        self.assertEqual(
            self.template_with_variants.demand_period_info[key]["value"], 15.0
        )
        self.assertEqual(
            self.template_with_variants.demand_period_info[key]["name"], "Last 7 days"
        )

    def test_demand_two_periods_enabled(self):
        """With two active periods, demand is computed per period (e.g. 7d vs 30d)."""
        self.period_7d.active = True
        self.period_last_30_days.active = True
        self._create_outgoing_move(self.product, self.today - timedelta(days=5), 10.0)
        self._create_outgoing_move(self.product, self.today - timedelta(days=20), 5.0)
        self.product.invalidate_recordset(["demand_period_info"])
        key_7d = str(self.period_7d.id)
        key_30d = str(self.period_last_30_days.id)
        self.assertIn(key_7d, self.product.demand_period_info)
        self.assertIn(key_30d, self.product.demand_period_info)
        self.assertEqual(self.product.demand_period_info[key_7d]["value"], 10.0)
        self.assertEqual(self.product.demand_period_info[key_30d]["value"], 15.0)
        self.assertEqual(self.product.demand_period_info[key_7d]["name"], "Last 7 days")
        self.assertEqual(
            self.product.demand_period_info[key_30d]["name"], "Last 30 days"
        )
