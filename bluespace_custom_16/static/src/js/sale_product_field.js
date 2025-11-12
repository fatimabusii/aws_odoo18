/** @odoo-module alias=@bluespace_custom_16/js/date_validation **/

import { patch } from "@web/core/utils/patch";
import { serializeDateTime } from "@web/core/l10n/dates";
import { SaleOrderLineProductField } from '@sale/js/sale_product_field';


patch(SaleOrderLineProductField.prototype, 'bluespace_custom_16', {

    async _openRentalConfigurator(edit) {
        console.log("_openRentalConfigurator@@@@@@@@@@@@@:::iiiiiiiiiiiiiiii:")
        /*this.action.doAction(
            'sale_renting.rental_configurator_action',
            {
                additionalContext: this._defaultRentalData(edit),
                onClose: async (closeInfo) => {
                    const record = this.props.record;
                    if (closeInfo && !closeInfo.special) {
                        record.update(closeInfo.rentalConfiguration);
                    } else {
                        if (!record.data.start_date || !record.data.return_date) {
                            record.update({
                                product_id: false,
                                name: '',
                            });
                        }
                    }
                }
            }
        );*/
    },
});
