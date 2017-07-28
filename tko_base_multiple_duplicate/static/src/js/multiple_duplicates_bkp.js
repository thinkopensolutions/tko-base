odoo.tko_base_multiple_duplicate = function(session) {
    var _t = session.web._t;
    var has_action_id = false;

    function launch_wizard(self, view, user_type, email) {
        var action = view.getParent().action;
        var Duplicate = new session.web.DataSet(self, 'multiple.duplicates', view.dataset.get_context());
        var domain = new session.web.CompoundDomain(view.dataset.domain);
        if (view.fields_view.type == 'form') {
            domain = new session.web.CompoundDomain(domain, [['id', '=', view.datarecord.id]]);
        }
        if (view.fields_view.type == 'form') rec_name = view.datarecord.name;
        else rec_name = '';
        session.web.pyeval.eval_domains_and_contexts({
            domains: [domain],
            contexts: [Duplicate.get_context()]
        }).done(function (result) {
            Duplicate.create({
                name: 1,
                active_model: view.dataset.model,
                active_id : view.datarecord.id,
            }).done(function(share_id) {
                var step1 = Duplicate.call('go_step_1', [[share_id], Duplicate.get_context()]).done(function(result) {
                    var action = result;
                    self.do_action(action);
                });
            });
        });
    }



    /* Extend the Sidebar to add Multiple Duplicate  links in the 'More' menu */
    session.web.Sidebar = session.web.Sidebar.extend({

        start: function () {
            var self = this;
            this._super(this);
			var view = this.getParent()
			var wizard_label = 'Multiple Duplication';
			if (view.dataset.model === 'account.invoice'){
				wizard_label = 'Invoice Duplication'
			}
			//add attachment only in form view
			if (view.fields_view.type == 'form')
				{
		            self.add_items('other', [{
			                label: _t(wizard_label),
			                callback: self.on_click_multiple_duplicate,
			                classname: 'oe_share'
			            },
			            ]);
				}
       		 },

        on_click_multiple_duplicate: function (item) {
            var view = this.getParent()
            launch_wizard(this, view, 'emails', false);
        },
        
        on_click_download: function (item) {
            var view = this.getParent()
            launch_wizard(this, view, 'emails', false);
        },


    });


};