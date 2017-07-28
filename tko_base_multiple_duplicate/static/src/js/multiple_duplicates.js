odoo.define('tko_base_multiple_duplicate.multiple_duplicates', function(require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');
    var Model = require("web.Model");
    var _t = core._t;

    function launch_wizard(self, context) {
            var call_obj = new Model('multiple.duplicates')
            //open tree view for the model
            openerp.webclient.action_manager.do_action({
                name: "Multiple Duplicates",
                views: [[false, 'form']],
                target: 'new',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'multiple.duplicates',
                context: context,
            });
        }


    FormView.include({
        render_sidebar: function($node) {

            this._super.apply(this, arguments);
            var wizard_label = 'Multiple Duplication';
            if (this.model === 'account.invoice'){
				wizard_label = 'Invoice Duplication'
			}
            if (this.sidebar) {
                this.sidebar.add_items('other', _.compact([
                    this.is_action_enabled('delete') && {
                        label: _t(wizard_label),
                        callback: this.on_click_multiple_duplicate
                    },
                ]));

            }
        },
        on_click_multiple_duplicate: function(item) {
            var view = this.getParent()
            this.dataset.context.params.active_id = this.datarecord.id;
            this.dataset.context.params.active_model = this.dataset.model;
            launch_wizard(this, this.dataset.context.params || {'active_id' : this.datarecord.id, 'active_model' : this.dataset.model});
        },
    });

});