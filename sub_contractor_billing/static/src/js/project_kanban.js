odoo.define('sub_contractor_billing.project_kanban', function (require) {
'use strict';

var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
     // YTI TODO: Should be transformed into a extend and specific to project
    _openRecord: function () {
        console.log('rrrrrrr')
        console.log(this)
        this._super.apply(this, arguments);
        
    },
});


});