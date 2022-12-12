# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class PrintingAutoMixin(models.AbstractModel):
    _name = "printing.auto.mixin"
    _description = "Printing Auto Mixin"

    printing_auto_error = fields.Text("Printing error")

    def _on_printing_auto_start(self):
        self.write({"printing_auto_error": False})

    def _printing_auto_done_post(self, auto, printer, count):
        self.ensure_one()
        self.message_post(
            body=_("{name}: {count} document(s) sent to printer {printer}").format(
                name=auto, count=count, printer=printer
            )
        )

    def _on_printing_auto_done(self, auto, printer, count):
        self._printing_auto_done_post(auto, printer, count)

    def _on_printing_auto_error(self, e):
        self.write({"printing_auto_error": str(e)})

    def send_documents_to_printer(self):
        """Print some report or attachment directly to the corresponding printer."""
        self._on_printing_auto_start()
        for record in self:
            for auto in record.auto_printing_ids:
                try:
                    with self.env.cr.savepoint():
                        printer, count = auto.do_print(record)
                        if count:
                            record._on_printing_auto_done(auto, printer, count)
                except Exception as e:
                    _logger.exception(
                        "An error occurred while printing '%s' for record %s.",
                        auto,
                        record,
                    )
                    record._on_printing_auto_error(e)
