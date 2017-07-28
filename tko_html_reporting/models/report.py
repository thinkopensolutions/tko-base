# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.report.models import report
import logging
import re
import time
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportHTML(report.Report):
    # _inherit = "report"
    _description = "Report"

    # This method returns raw text from the given template,
    # substituting variable, python expressions and methods
    def render_html_template(self, object, text):
        if text:
            # user can use o instead of object to access fields of object
            o = object
            pattern = re.compile('\$\{(.+?)\}s')
            expression_matches = pattern.findall(str(text.encode('utf-8')))
            for expression in expression_matches:
                error_label = 'Invalid Variable or Python Expression'
                try:
                    value = eval(expression)
                    text = text.replace(
                        '${' + expression + '}s',
                        value)
                except:
                    try:
                        value = (
                                    '<font color="red"><strong>[ERROR: %s : %s]<strong></font>') % (
                                    error_label, expression)
                    except Exception as err:
                        value = err
                    text = text.replace(
                        '${' + expression + '}s',
                        value)
                    _logger.error(
                        ("ERROR: %s %s") %
                        (error_label, expression))
                    # evaluate object variables
                    # this case will be used only for image, above method can't print images with binary data
                    # evaluate python expression
                    # python expression would use {}
                    # eg: ${time.strftime("%d de %B de %Y").decode("utf-8")}s
                    # we can't use same bracket
                    # because we need to match variables and expressions separately
                    # because we need to treat them differently
                    # in case of we use same bracket for both of them
                    # there is a chance we start matching with the $( of variable and ending
                    # on )s or )p of expression
                    # which is wrong
            variable_patterns = re.compile('\$\((.*?)\)s')
            matches = variable_patterns.findall(str(text.encode('utf-8')))
            value = ''
            type = ''
            for match in matches:
                value = object
                block = match.split(',')
                for field in block[0].split('.'):
                    try:
                        type = value._fields[field].type
                        if type != 'selection':
                            value = value[field]
                        else:
                            # get label for selection field
                            value = str(unicode(dict(value.fields_get(allfields=[field])[field]['selection'])[
                                                    value[field]]).encode('utf-8'))
                    except Exception as err:
                        value = (
                                    '<font color="red"><strong>[ERROR: Field %s doesn\'t exist  in %s]<strong></font>') % (
                                    err, value)
                        _logger.error(
                            ("Field %s doesn't exist  in %s") %
                            (err, value))
                if value:
                    if type != 'binary':
                        try:
                            text = text.replace(
                                '$(' + match + ')s',
                                unicode(value))
                        except:
                            text = text.replace(
                                '$(' + match + ')s',
                                unicode(value, 'utf-8'))

                    else:
                        width, height = '', ''
                        try:
                            if block[1]:
                                width = ' width="%spx"' % block[1]
                            if block[2]:
                                height = ' height="%spx"' % block[2]
                            text = text.replace(
                                '$(' + match + ')s',
                                '<img src="data:image/jpeg;base64,' + str(value) + '"%s%s/>' %
                                (width, height))
                        except Exception as err:
                            value = _(
                                u'<font color="red"><strong>[ERROR: Wrong image size indication in "%s". Examples: "(partner_id.image,160,160)" or "(partner_id.image,,160)" or "(partner_id.image,160,)" or "(partner_id.image,,)"]<strong></font>' %
                                match)
                            _logger.error(
                                _(
                                    u'Wrong image size indication in "$(%s)s". Examples: $(partner_id.image,160,160)s or $(partner_id.image,,160)s or $(partner_id.image,160,)s or $(partner_id.image,,)s' % match))
                            text = text.replace(
                                '$(' + match + ')s', str(value))

                if not value:
                    text = text.replace('$(' + match + ')s', '')
            return text

    # This method runs only for report type html-pdf
    # otherwise it returns super
    @api.model
    def get_html(self, docids, report_name, data=None):
        context = dict(self._context or {})
        if data.get('report_type') == u'html-pdf':

            # if context.get('active_model') and context.get('active_id'):
            #     object = self.env[self.get('active_model')].browse(context.get('active_id'))
            # else:
            #     raise Warning(u'Active model or Active ID not available')
            self._cr.execute("SELECT * FROM ir_act_report_xml WHERE report_name=%s", (report_name,))
            row = self._cr.dictfetchone()
            template_id = row['template_id']
            object = self.env[context.get('active_model')].browse(context.get('active_id'))
            template = self.env['html.report.template'].browse(template_id)
            header = body = footer = ''
            if template.report_header:
                header = self.render_html_template(object, template.report_header)
            if template.report_body:
                body = self.render_html_template(object, template.report_body)
            if template.report_footer:
                footer = self.render_html_template(object, template.report_footer)

            html = u'''
<t t-call="report.html_container">
   <t t-foreach="docs" t-as="o">
      <t>
         <div class="header">
            %s
         </div>
      </t>
      <!-- Report Body -->
      <div class="page">
         <div class="row">
         <style type="text/css">
            %s
        </style>
            %s
         </div>
      </div>
      <!-- Report Footer -->
      <t">
         <div class="footer">
            %s
         </div>
      </t>
   </t>
</t>''' % ( header, template.report_css, body, footer)
            return html.encode('utf-8').strip()
        else:
            # TODO
            # NOT RETURNING SUPER because it falls back on
            # this method not calling method of super class
            report_model_name = 'report.%s' % report_name
            report_model = self.env.get(report_model_name)

            if report_model is not None:
                return report_model.render_html(docids, data=data)
            else:
                report = self._get_report_from_name(report_name)
                docs = self.env[report.model].browse(docids)
                docargs = {
                    'doc_ids': docids,
                    'doc_model': report.model,
                    'docs': docs,
                }
                return self.render(report.report_name, docargs)
