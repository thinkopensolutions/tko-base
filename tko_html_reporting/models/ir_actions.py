# -*- coding: utf-8 -*-
import datetime
import dateutil
import logging
import os
import time
from pytz import timezone

from odoo import api, fields, models, tools, workflow, _
from odoo.exceptions import MissingError, UserError, ValidationError
from odoo.report.report_sxw import report_sxw, report_rml
from odoo.tools.safe_eval import safe_eval, test_python_expr

_logger = logging.getLogger(__name__)


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    template_id = fields.Many2one('html.report.template','Template')
    report_type = fields.Selection(selection_add=[('html-pdf', 'HTML - PDF')])

    _sql_constraints = [
        ('unique_report_name', 'UNIQUE(report_name)', u'Name of the report must be unique'),
    ]


    @api.onchange('template_id')
    def onchange_template_id(self):
        self.report_name = self.template_id.report_name or False

    @api.model
    def render_report(self, res_ids, name, data):
        """
        Look up a report definition and render the report for the provided IDs.
        """
        report = self._lookup_report(name)
        if data['report_type'] =='html-pdf':
            return self.env['report'].get_pdf(res_ids, report, data=data), 'pdf'
        else:
            return super(IrActionsReportXml, self).render_report(res_ids, name, data)

    @api.model_cr
    def _lookup_report(self, name):
        """
        Look up a report definition.
        """
        join = os.path.join

        self._cr.execute("SELECT * FROM ir_act_report_xml WHERE report_name=%s", (name,))
        row = self._cr.dictfetchone()
        if not row['report_type'] != 'pdf-html':
            return super(IrActionsReportXml, self)._lookup_report(name)
        else:
            return row['report_name']


