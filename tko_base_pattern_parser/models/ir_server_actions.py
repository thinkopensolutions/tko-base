# -*- coding: utf-8 -*-
import logging

from odoo.tools.safe_eval import safe_eval
from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    parser_agent_id = fields.Many2one('pattern.parser.agent',
                                      ondelete='cascade',
                                      string='Parser Agent',
                                      help='Parser Agent.')

    @api.model
    def _get_states(self):
        res = super(IrActionsServer, self)._get_states()
        res.insert(0, ('parser', 'Pattern Parser'))
        return res

    @api.model
    def run_action_parser_multi(self, action, eval_context=None):
        if self.parser_agent_id:
            self.parser_agent_id._parse(eval_context['records'])
        return False
