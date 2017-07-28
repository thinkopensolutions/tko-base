# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HtmlReportTemplate(models.Model):
    _name = 'html.report.template'


    name = fields.Char(u'Name', required=True)
    report_name = fields.Char(u'Report Name', required=True)
    report_header = fields.Html(u'Report Header')
    report_body = fields.Html(u'Report',required =True)
    report_footer = fields.Html(u'Report Footer')
    model_id = fields.Many2one('ir.model',u'Model')
    report_css = fields.Text(u'CSS')
    background_image = fields.Char('Back Ground')
    report_id = fields.Many2one('ir.actions.report.xml',compute='_get_linked_report',string=u'Report', help=u'Linked report with this template')

    sql_constraints = [
        ('unique_report_name', 'UNIQUE(report_name)', u'Name of the report must be unique'),
    ]


    @api.one
    def _get_linked_report(self):
        template = self.env['ir.actions.report.xml'].search([('template_id','=',self.id)], limit=1)
        self.report_id = template and template.id or False

    @api.multi
    def create_report(self):
        self.env['ir.actions.report.xml'].create({
            'name' : self.name,
            'report_name' : self.report_name,
            'report_type' : 'html-pdf',
            'template_id' : self.id,
            'model' : self.model_id.model,
        })

    @api.multi
    def unlink(self):
        for record in self:
            if record.report_id:
                record.report_id.unlink()
        return super(HtmlReportTemplate, self).unlink()

    @api.multi
    def write(self, vals):
        result = super(HtmlReportTemplate, self).write(vals)
        for record in self:
            if record.report_id:
                vals_dict = {'name' : record.name,
            'report_name' : self.report_name,
            'report_type' : 'html-pdf',
            'template_id' : self.id,
            'model' : self.model_id.model}
                record.report_id.write(vals_dict)
        return result

