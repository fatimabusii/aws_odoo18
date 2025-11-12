/** @odoo-module alias=@bluespace_custom_16/js/date_validation **/

import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events, {
        'click .account-submit': '_onClickAccountSubmit',
    }),
    /**
     * Toggles the add to cart button depending on the possibility of the
     * current combination.
     *
     * @override
     */
    _submitForm: function () {
        const params = this.rootProduct;
        const $product = $('#product_detail');
        const productTrackingInfo = $product.data('product-tracking-info');
        if (productTrackingInfo) {
            productTrackingInfo.quantity = params.quantity;
            $product.trigger('add_to_cart_event', [productTrackingInfo]);
        }

        params.add_qty = params.quantity;
        const move_in_date = $('#MoveInDate').val();
        const move_out_date = $('#MoveOutDate').val();
        console.log("MOVEEEEEEEEEE OUTTTTTTTTT", move_in_date)
        const is_move_out_date = $('input[name="is_no_move_out_date"]').is(':checked');
        const flexible_move_out = $('input[name="is_move_out_date"]').is(':checked');
        const no_of_visitors = $('input[name="ofc_person"]').val();
        /*#const is_move_out_date = $('.is_no_move_out_date').val();*/
        console.log("MOVEEEEEEEEEE", is_move_out_date)
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        params.move_in_date = move_in_date;
        params.move_out_date = move_out_date;
        params.is_move_out_date = is_move_out_date
        params.flexible_move_out = flexible_move_out
        params.no_of_visitors = no_of_visitors
        console.log("HELLOOOOOOOO", params)
        delete params.quantity;
        return this.addToCart(params);
    },

    _onClickAccountSubmit: function (ev, forceSubmit) {
        console.log("_onClickAccountSubmit>>>>>>>>>>>>>>>>>>>")
        if ($(ev.currentTarget).is('#add_to_cart, #products_grid .account-submit') && !forceSubmit) {
            return;
        }
        var $aSubmit = $(ev.currentTarget);
        if (!ev.isDefaultPrevented() && !$aSubmit.is(".disabled")) {
            ev.preventDefault();
            $aSubmit.closest('form').submit();
        }
        if ($aSubmit.hasClass('a-submit-disable')) {
            $aSubmit.addClass("disabled");
        }
        if ($aSubmit.hasClass('a-submit-loading')) {
            var loading = '<span class="fa fa-cog fa-spin"/>';
            var fa_span = $aSubmit.find('span[class*="fa"]');
            if (fa_span.length) {
                fa_span.replaceWith(loading);
            } else {
                $aSubmit.append(loading);
            }
        }
    },
});
