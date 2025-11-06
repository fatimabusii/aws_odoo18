odoo.define('website_extra_info.payment_form', require => {
    'use strict';

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');
    const PaymentMixin = {

        _onClickPaymentOption: function (ev) {
            const checkedRadio = $(ev.currentTarget).find('input[name="o_payment_radio"]')[0];
            $(checkedRadio).prop('checked', true);
            const provider = this._getProviderFromRadio(checkedRadio);
            if (provider !='iveri')
                $("#eft_display").show();
            else
                $("#eft_display").hide();
            //this._super.apply(ev);
            this._showInputs();

            // Disable the submit button while building the content
            this._disableButton(false);

            /*var eft = document.getElementById("eft_display_ofc").innerText;
            if (eft && provider !='iveri') {
                this._hideInputs();
                this._disableButton(true);
            }
            else {
                this._showInputs();
                this._disableButton(false);
            }*/

            // Unfold and prepare the inline form of selected payment option
            this._displayInlineForm(checkedRadio);

            // Re-enable the submit button
            this._enableButton();
        },

    };
    checkoutForm.include(PaymentMixin);
    manageForm.include(PaymentMixin);
});
