# -*- coding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Mail Modules',
    'summary': '',
    'description': 'Installs mail related modules that enhance user usability.',
    'author': 'TKO',
    'category': 'Discuss',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-uk.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
    ],
    'external_dependencies': {
                                'python': [],
                                'bin': [],
                                },
    'init_xml': [],
    'update_xml': [
        'views/ir_actions_view.xml',
        'views/report_template_view.xml',
    ],
    'css': [],
    'demo_xml': [],
    'test': [],
    'data': [
    ],
}
