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

    @api.multi
    def run(self):
        # redefine to call predict only once with all active_ids
        res = False
        for action in self:
            eval_context = self._get_eval_context(action)
            condition = action.condition
            if hasattr(self, 'run_action_%s' % action.state) and action.state == 'parser':
                active_id = self._context.get('active_id')
                active_ids = self._context.get('active_ids', [active_id] if active_id else [])
                # run context dedicated to a particular active_id
                run_self = self.with_context(active_ids=[active_id], active_id=active_id)
                eval_context["context"] = run_self._context
                expr = safe_eval(str(condition), eval_context)
                if not expr:
                    continue
                # call the single method related to the action: run_action_<STATE>
                func = getattr(run_self, 'run_action_%s' % action.state)
                res = func(action, eval_context=eval_context)
            # This line makes Galalai and Parser compatible
            # we don't want to call super in case of Galalai and Parser
            if action.state not in ['parser', 'predict']:
                return super(IrActionsServer, action).run()
        return res

    @api.model
    def run_action_parser(self, action, eval_context=None):
        if self.parser_agent_id:
            self.parser_agent_id._parse(eval_context['records'])
        return False
