import logging

from odoo.exceptions import UserError
from odoo.tests import common

logger = logging.getLogger(__name__)


class TestAutoPrinting(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server = cls.env["printing.server"].create({})
        cls.stock_picking = cls.env.ref("stock.outgoing_shipment_main_warehouse")
        cls.printer_1 = cls.env["printing.printer"].create(
            {
                "name": "Printer",
                "server_id": cls.server.id,
                "system_name": "Sys Name",
                "default": True,
                "status": "unknown",
                "status_message": "Msg",
                "model": "res.users",
                "location": "Location",
                "uri": "URI",
            }
        )
        cls.report = cls.env.ref("stock.action_report_delivery")
        cls.auto_printing = cls.env["printing.auto"].create(
            {
                "name": "Auto Printing 1",
                "picking_type_id": cls.stock_picking.picking_type_id.id,
                "report_id": cls.report.id,
                "printer_id": cls.printer_1.id,
            }
        )
        cls.auto_printing_2 = cls.env["printing.auto"].create(
            {
                "name": "Auto Printing 2",
                "picking_type_id": cls.stock_picking.picking_type_id.id,
                "printer_id": cls.printer_1.id,
                "file_type": "attachment",
            }
        )
        cls.report_datas, a = cls.report.with_context(
            must_skip_send_to_printer=True,
        )._render_qweb_pdf(cls.stock_picking.id)
        cls.attachment_1 = cls.env["ir.attachment"].create(
            {
                "name": "attachment_1.pdf",
                "res_model": "stock.picking",
                "res_id": cls.stock_picking.id,
                "raw": cls.report_datas,
            }
        )
        cls.tray = cls.env["printing.tray"].create(
            {
                "name": "Tray",
                "system_name": "TrayName",
                "printer_id": cls.printer_1.id,
            }
        )

    def test_00_test_general(self):
        with self.assertRaises(UserError):
            self.stock_picking.send_documents_to_printer()

    def test_10_test_print_report(self):
        with self.assertRaises(UserError):
            self.auto_printing.do_print(self.stock_picking)

    def test_20_test_print_attachment(self):
        with self.assertRaises(UserError):
            self.auto_printing_2.do_print(self.stock_picking)

    def test_30_test_condition_filter(self):
        self.auto_printing.condition = [("id", "=", self.stock_picking.id)]
        auto_printing = self.auto_printing._check_condition(self.stock_picking)
        self.assertEqual(auto_printing, self.stock_picking)

        self.auto_printing.condition = [("id", "=", 0)]
        auto_printing = self.auto_printing.check_condition(self.stock_picking)
        self.assertEqual(len(auto_printing), 0)

    def test_40_test_attachment_filter(self):
        attachment_2 = self.env["ir.attachment"].create(
            {
                "name": "attachment_2.pdf",
                "res_model": "stock.picking",
                "res_id": self.stock_picking.id,
                "datas": self.report_datas,
            }
        )
        self.auto_printing.attachment_domain = [("id", "=", attachment_2.id)]
        test_attachment = self.auto_printing.generate_data_from_attachments(
            self.stock_picking
        )
        self.assertEqual(len(test_attachment), 1)
        self.assertEqual(self.report_datas, test_attachment[0])

    def test_50_test_field_object(self):
        self.auto_printing.field_object = "picking_type_id"
        field_object = self.auto_printing._get_record(self.stock_picking)
        self.assertEqual(field_object, self.stock_picking.picking_type_id)

    def test_50_test_printer_and_behaviour(self):
        self.assertEqual(
            self.auto_printing.get_behaviour()["printer"],
            self.auto_printing.printer_id,
        )

        self.auto_printing.printer_id = None

        self.assertEqual(
            self.auto_printing.get_behaviour(),
            self.report.behaviour(),
        )

        behaviour = self.auto_printing_2.get_behaviour()
        self.assertEqual(behaviour["printer"], self.auto_printing_2.printer_id)
        self.assertFalse(behaviour["tray"])

        self.auto_printing_2.printer_tray_id = self.tray
        behaviour = self.auto_printing_2.get_behaviour()
        self.assertEqual(behaviour["printer"], self.auto_printing_2.printer_id)
        self.assertEqual(behaviour["tray"], self.tray.system_name)

        self.auto_printing_2.printer_tray_id = None
        self.auto_printing_2.printer_id = None

        behaviour_test = self.env[
            "ir.actions.report"
        ]._get_user_default_print_behaviour()
        behaviour = self.auto_printing_2.get_behaviour()
        self.assertEqual(behaviour, behaviour_test)

    def test_60_output(self):
        # Report
        for content in self.auto_printing.get_content(self.stock_picking):
            self.assertTrue(self._check_pdf(content))

        # Attachments
        attachment_prefix = "ir_attachment"
        attachment_names = []
        attachment_len = 2
        for i in range(attachment_len):
            attachment_name = "{name}_{i}".format(i=i, name=attachment_prefix)
            attachment_names.append(attachment_name)
            self.env["ir.attachment"].create(
                {
                    "name": attachment_name,
                    "res_id": self.stock_picking.id,
                    "res_model": self.stock_picking._name,
                    "raw": content,
                }
            )
        self.auto_printing_2.attachment_domain = [("name", "in", attachment_names)]
        contents = self.auto_printing_2.get_content(self.stock_picking)
        self.assertEqual(len(contents), attachment_len)
        for content in contents:
            self.assertTrue(self._check_pdf(content))

    def _check_pdf(self, content):
        return "<span>WH/OUT/00001</span>" in str(content)
