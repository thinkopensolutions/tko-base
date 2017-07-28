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

from odoo import fields, api, models

_logger = logging.getLogger(__name__)


class MultipleDuplicates(models.TransientModel):
    _name = 'multiple.duplicates'

    name = fields.Integer('Duplicate in')

    @api.multi
    def duplicate_records(self):
        context = dict(self._context)
        self.ensure_one()
        new_invs = []
        res_model = context.get('active_model')
        res_id = context.get('active_id')
        if res_model and res_id:
            for i in range(0, self.name):
                new_inv = self.env[res_model].browse(res_id).copy()
                new_invs.append(new_inv.id)
                _logger.info("Duplicating record %s for model %s %s time" % (res_id, res_model, i + 1))
            return {
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': res_model,
                'domain': [('id', 'in', new_invs)],
                'type': 'ir.actions.act_window',
            }
