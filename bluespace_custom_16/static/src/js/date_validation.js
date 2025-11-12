/** @odoo-module **/
/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

console.log("Initializing Hover Modals Widget");

publicWidget.registry.HoverModalsWidget = publicWidget.Widget.extend({
    selector: "#wrapwrap",

    events: {
        "click a.modal-link": "_onLinkClick",
        // "mouseleave a.modal-link": "_onLinkLeave",
    },

    // _onLinkHover: function (ev) {
    //     ev.preventDefault();
    //     const modalId = $(ev.currentTarget).data("modal");
    //     console.log("Hovering over link, showing modal:", modalId);

    //     const modalEl = $("#" + modalId);
    //     if (modalEl.length) {
    //         modalEl.modal("show");
    //     } else {
    //         console.error("Modal not found for id:", modalId);
    //     }
    // },

    // _onLinkLeave: function (ev) {
    //     const modalId = $(ev.currentTarget).data("modal");
    //     console.log("Mouse left link, hiding modal:", modalId);

    //     const modalEl = $("#" + modalId);
    //     if (modalEl.length) {
    //         modalEl.modal("hide");
    //     }
    // },
    _onLinkClick: function (ev) {
        ev.preventDefault();

        const modalId = $(ev.currentTarget).data("modal");
        console.log("Clicked link, showing modal:", modalId);

        const modalEl = $("#" + modalId);
        if (modalEl.length) {
            modalEl.modal("show");  // Bootstrap handles overlay and focus
        } else {
            console.error("Modal not found for id:", modalId);
        }
    },
});
