odoo.define('pos.printbill', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');

    var QWeb = core.qweb;

    var ReceiptScreenWidget = screens.ReceiptScreenWidget.extend({
        render_receipt: function() {
            this._super();
            var order = this.pos.get_order();
            this.$('.pos-bill-categ-receipt-container').html(QWeb.render('PosTicket_Bill_Category', {
                widget: this,
                order: order,
                receipt: order.export_for_printing(),
                bill_orderlines: order.get_bill_orderlines(),
                orderlines: order.get_orderlines(),
                paymentlines: order.get_paymentlines(),
            }));
        },
    });
    gui.define_screen({
        name: 'receipt',
        widget: ReceiptScreenWidget
    });

    models.load_fields("product.product", "bill_category");

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        get_bill_orderlines: function() {
            var order_id = this.pos.get_order().get_orderlines();

            var bill_categs = []
            _(this.pos.get_order().get_orderlines()).map(function(result) {
                if (result.product.bill_category != false) {
                    for (var i = 0; i < bill_categs.length; i++) {
                        if (bill_categs[i].name == result.product.bill_category[1]) {
                            bill_categs[i].orderlines.push(result);

                            return;
                        }
                    }
                    bill_categs.push({
                        'name': result.product.bill_category[1],
                        'orderlines': [result]
                    });
                }
            });
            return bill_categs;
        },
    });
});