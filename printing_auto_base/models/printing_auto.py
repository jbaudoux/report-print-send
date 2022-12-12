# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class PrintingAuto(models.Model):
    _name = "printing.auto"
    _description = "Printing Auto"

    name = fields.Char(string="Name", required=True)
    file_type = fields.Selection(
        [
            ("report", "Report"),
            ("attachment", "Attachment"),
        ],
        string="Type",
        default="report",
        required=True,
        help=(
            "Choose to print the result of an odoo report or a pre-existing "
            "attachment (useful for labels received from carriers that are "
            "recorded on the picking as an attachment)"
        ),
    )
    field_object = fields.Char(
        "Object", help="Select on which document the report must be executed"
    )

    report_id = fields.Many2one("ir.actions.report")

    attachment_domain = fields.Char("Attachment", default="[]")
    condition = fields.Char(
        "Condition",
        default="[]",
        help="Give a domain that must be valid for printing this",
    )

    printer_id = fields.Many2one("printing.printer", string="Printer")
    printer_tray_id = fields.Many2one("printing.tray")
    nbr_of_copies = fields.Integer("Number of Copies", default=1)

    label = fields.Boolean(string="Is Label")

    @api.constrains("report_id", "file_type")
    def check_report(self):
        for rec in self:
            if rec.file_type == "report" and not rec.report_id:
                raise UserError(_("Report was not set"))

    def do_print(self, record):
        self.ensure_one()
        record.ensure_one()

        behaviour = self.get_behaviour()
        printer = behaviour["printer"]
        if not printer:
            raise UserError(
                _("No printer configured to print this {}.").format(self.name)
            )

        if self.nbr_of_copies <= 0:
            return (printer, 0)
        if not self._check_condition(record):
            return (printer, 0)

        count = 0
        record = self._get_record(record)
        for content in self._get_content(record):
            for _n in range(self.nbr_of_copies):
                printer.print_document(report=None, content=content, **behaviour)
                count += 1
        return (printer, count)

    def get_behaviour(self):
        if self.printer_id:
            tray = self.printer_tray_id and self.printer_tray_id.system_name
            return {"printer": self.printer_id, "tray": tray}
        if self.file_type == "report":
            return self.report_id.behaviour()
        if self.label:
            return {"printer": self.env.user.default_label_printer_id}
        return self.env["ir.actions.report"]._get_user_default_print_behaviour()

    def _get_record(self, record):
        if self.field_object:
            try:
                return safe_eval(f"obj.{self.field_object}", {"obj": record})
            except Exception as e:
                raise ValidationError(
                    _("The Object field could not be applied because: %s") % str(e)
                ) from e
        return record

    def _check_condition(self, record):
        domain = safe_eval(self.condition, {"env": self.env})
        return record.filtered_domain(domain)

    def _get_content(self, record):
        if self.file_type == "report":
            return [self.generate_data_from_report(record)]
        if self.file_type == "attachment":
            return self.generate_data_from_attachments(record)
        return []

    def _prepare_attachment_domain(self, record):
        domain = safe_eval(self.attachment_domain)
        record_domain = [
            ("res_id", "=", record.id),
            ("res_model", "=", record._name),
        ]
        return expression.AND([domain, record_domain])

    def generate_data_from_attachments(self, record):
        domain = self._prepare_attachment_domain(record)
        attachments = self.env["ir.attachment"].search(domain)
        if not attachments:
            raise ValidationError(_("No attachment was found."))
        return [base64.b64decode(a.datas) for a in attachments]

    def generate_data_from_report(self, record):
        self.ensure_one()
        data, _ = self.report_id.with_context(
            must_skip_send_to_printer=True
        )._render_qweb_pdf(record.id)
        return data
