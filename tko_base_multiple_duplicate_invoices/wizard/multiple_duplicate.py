# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen - Portugal & Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import _
from odoo import fields, api, models
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

_logger = logging.getLogger(__name__)

interval_dict = {'d': 'days',
                 'w': 'weeks',
                 'm': 'months',
                 'y': 'years',
                 }


class multiple_duplicates(models.TransientModel):
    _inherit = 'multiple.duplicates'

    interval = fields.Integer('Interval to compute due date and invoice date')
    interval_unit = fields.Selection([('d', 'Days'), ('w', 'Weeks'), ('m', 'Months'), ('y', 'Years')], default='d',
                                     required=True, string='Time between due dates')

    @api.multi
    def duplicate_records(self):
        context = dict(self._context)
        new_invs = []
        res_model = context.get('active_model')
        res_id = context.get('active_id')
        if res_model and res_id and res_model == 'account.invoice':
            invoice = self.env['account.invoice'].browse(res_id)
            if not invoice.date_due:
                raise Warning(_('Please define due date for selected invoice'))
            base_date_due = invoice.date_due
            next_invoice_date = False
            base_invoice_date = invoice.date_invoice
            interval_unit = self.interval_unit
            days = weeks = months = years = 0
            for i in range(0, self.name):
                if interval_unit == 'd':
                    days = self.interval
                if interval_unit == 'm':
                    months = self.interval
                if interval_unit == 'w':
                    weeks = self.interval
                if interval_unit == 'y':
                    years = self.interval
                if base_invoice_date:
                    next_invoice_date = datetime.strptime(str(base_invoice_date), DF).date() + relativedelta(days=days,
                                                                                                         weeks=weeks,
                                                                                                         months=months,
                                                                                                         years=years)
                next_date_due = datetime.strptime(str(base_date_due), DF).date() + relativedelta(days=days,
                                                                                                 weeks=weeks,
                                                                                                 months=months,
                                                                                                 years=years)
                new_inv = self.env[res_model].browse(res_id).copy(
                    {'date_due': next_date_due, 'invoice_date': next_invoice_date})
                new_invs.append(new_inv.id)
                if base_invoice_date:
                    base_invoice_date = next_invoice_date
                base_date_due = next_date_due
                _logger.info("Duplicating invoice %s wtih emission date %s, %s time " % (
                    invoice.name, next_date_due, i + 1))
            return {
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': res_model,
                'domain': [('id', 'in', new_invs)],
                'type': 'ir.actions.act_window',
            }
        else:
            return super(multiple_duplicates, self).duplicate_records()
