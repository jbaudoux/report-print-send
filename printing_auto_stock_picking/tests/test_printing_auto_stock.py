# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.exceptions import UserError

from odoo.addons.printing_auto_base.tests.common import (
    PrintingPrinter,
    TestPrintingAutoCommon,
    print_document,
)


@mock.patch.object(PrintingPrinter, "print_document", print_document)
class TestAutoPrinting(TestPrintingAutoCommon):
    @classmethod
    def setUpReportAndRecord(cls):
        cls.report = cls.env.ref("stock.action_report_delivery")
        cls.record = cls.env.ref("stock.outgoing_shipment_main_warehouse")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.printing_auto = cls._create_printing_auto_attachment()
        cls._create_attachment(cls.record, cls.data, "1")

    def test_action_done_printing_auto(self):
        self.record.picking_type_id.auto_printing_ids |= self.printing_auto
        self.printing_auto.printer_id = self.printer_1
        self.record._action_done()
        self.assertFalse(self.record.printing_auto_error)

    def test_action_done_printing_error(self):
        self.record.picking_type_id.auto_printing_ids |= self.printing_auto
        self.record._action_done()
        self.assertTrue(self.record.printing_auto_error)

    def test_action_done_printing_error_raise(self):
        self.record.picking_type_id.auto_printing_ids |= self.printing_auto
        self.printing_auto.action_on_error = "raise"
        with self.assertRaises(UserError):
            self.record._action_done()
