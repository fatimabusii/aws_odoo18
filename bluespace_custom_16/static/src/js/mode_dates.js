// /** @odoo-module **/

// import { Component, onMounted } from "@odoo/owl";
// import { registry } from "@web/core/registry";
// import { rpc } from "@web/core/network/rpc";

// export class MoveDatePicker extends Component {
//     static template = "bluespace_custom_16.MoveDatePicker";

//     setup() {
//         onMounted(() => {
//             this.initMoveInPicker();
//             this.initMoveOutPicker();
//         });
//     }

//     initMoveInPicker() {
//         const moveInEl = document.querySelector("#MoveInDate");
//         if (!moveInEl) return;

//         // initialize Flatpickr for move-in date
//         flatpickr(moveInEl, {
//             dateFormat: "m/d/Y",
//             minDate: "today",
//             onClose: async (selectedDates, dateStr) => {
//                 const dob = dateStr;
//                 if (!dob) return;

//                 const prodIsOffice = document.querySelector("#product_is_office")?.value;
//                 const prodIsBoardroom = document.querySelector("#product_is_boardroom")?.value;

//                 if (prodIsOffice || prodIsBoardroom) {
//                     this.handleOfficeMoveIn(dob);
//                 } else {
//                     this.handleStandardMoveIn(dob);
//                 }
//             },
//         });
//     }

//     async handleStandardMoveIn(dob) {
//         const moveOut = document.querySelector("#MoveOutDate")?.value;
//         if (moveOut) {
//             document.querySelector("#flexible_move_out_date")?.checked = false;
//             document.querySelector("#flexible_note")?.classList.add("d-none");
//             document.querySelector("#no_flexible_move_out_date")?.checked = false;
//             document.querySelector("#specific_move")?.classList.add("d-none");
//             document.querySelector("#specific_one_month")?.classList.add("d-none");
//             document.querySelector(".o_website_move_out_picker")?.classList.add("d-none");
//             document.querySelector("#MoveOutDate").value = "";
//         }

//         const moveDay = new Date(dob);
//         let rawInput1;
//         if (moveDay.getUTCDate() === 31) {
//             rawInput1 = new Date(moveDay.getFullYear(), moveDay.getMonth() + 1, 0);
//         } else if (moveDay.getUTCDate() + 1 >= 20) {
//             const nextMonth = new Date(moveDay.setMonth(moveDay.getMonth() + 1, 1));
//             rawInput1 = new Date(nextMonth.getFullYear(), nextMonth.getMonth() + 1, 0);
//         } else {
//             rawInput1 = new Date(moveDay.getFullYear(), moveDay.getMonth() + 1, 0);
//         }

//         $('input[name="renting_dates"]').daterangepicker({
//             startDate: dob,
//             endDate: rawInput1,
//         });

//         const prd_id = document.querySelector(".product_id")?.value;
//         try {
//             const result = await rpc("/bluespace/datevalidation", {
//                 dates: dob,
//                 prd_id,
//             });
//             $("#display").html(result.msg || "");
//         } catch (err) {
//             console.error("RPC error (datevalidation):", err);
//         }
//     }

//     async handleOfficeMoveIn(dob) {
//         const moveDay = new Date(dob);
//         const start_hours = parseInt($("#start_hours").val() || 7);
//         const start_minits = parseInt($("#start_minits").val() || 30);
//         const end_hours = parseInt($("#end_hours").val() || 18);
//         const end_minits = parseInt($("#end_minits").val() || 30);

//         function addMinutes(dt, minutes) {
//             return new Date(dt.getTime() + minutes * 60000);
//         }

//         const startDate = addMinutes(new Date(moveDay.setHours(start_hours)), start_minits);
//         const endDate = addMinutes(new Date(new Date(dob).setHours(end_hours)), end_minits);

//         $('input[name="renting_dates"]').daterangepicker({
//             startDate,
//             endDate,
//             timePicker: true,
//             timePicker24Hour: true,
//             locale: { format: "YYYY/MM/DD HH:mm" },
//         });

//         try {
//             const result = await rpc("/bluespace/daysvalidation", {
//                 in_date: startDate,
//                 out_date: endDate,
//             });
//             $("#display").html(result.msg || "");
//         } catch (err) {
//             console.error("RPC error (daysvalidation):", err);
//         }
//     }

//     initMoveOutPicker() {
//         const moveOutEl = document.querySelector("#MoveOutDate");
//         if (!moveOutEl) return;

//         flatpickr(moveOutEl, {
//             dateFormat: "F Y", // Month Year like "October 2025"
//             minDate: "today",
//             onClose: async (selectedDates, dateStr, instance) => {
//                 const moveIn = document.querySelector("#MoveInDate")?.value || "";
//                 const selected = selectedDates[0];
//                 if (!selected) return;

//                 try {
//                     const result = await rpc("/bluespace/specific_one_month", {
//                         move_in: moveIn,
//                         month_out: selected.getMonth(),
//                         year_out: selected.getFullYear(),
//                     });

//                     $("#specific_one_month").html(result.msg || "");
//                     if (result.msg) {
//                         $("#add_to_cart").addClass("disabled");
//                         $("#specific_move").hide(200);
//                     } else {
//                         $("#add_to_cart").removeClass("disabled");
//                         $("#specific_move").show(300);
//                     }
//                 } catch (err) {
//                     console.error("RPC error (specific_one_month):", err);
//                 }
//             },
//             onReady: (selectedDates, dateStr, instance) => {
//                 const now = new Date();
//                 instance.setDate(new Date(now.getFullYear(), now.getMonth(), 1));
//             },
//         });
//     }
// }

// registry.category("public_components").add("move_date_picker", MoveDatePicker);
/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class MoveDatePicker extends Component {
// static template = "bluespace_custom_16.MoveDatePicker";
setup() {
    console.log("[MoveDatePicker] setup() initializing...");
    onMounted(() => {
        console.log("[MoveDatePicker] Component mounted — initializing pickers");
        this.initMoveInPicker();
        this.initMoveOutPicker();
    });
}

// ---------------------- MOVE IN ----------------------
initMoveInPicker() {
    const moveInEl = document.querySelector("#MoveInDate");
    if (!moveInEl) {
        console.warn("[MoveInDate] element not found.");
        return;
    }

    console.log("[MoveInDate] Initializing Flatpickr...");
    flatpickr(moveInEl, {
        dateFormat: "m/d/Y",
        minDate: "today",
        // onClose: async (selectedDates, dateStr) => {
        //     console.log("[MoveInDate] onClose fired. Selected:", dateStr);
        //     const dob = dateStr;
        //     if (!dob) {
        //         console.warn("[MoveInDate] No date selected.");
        //         return;
        //     }

        //     const prodIsOffice = document.querySelector("#product_is_office")?.value;
        //     const prodIsBoardroom = document.querySelector("#product_is_boardroom")?.value;

        //     console.log("[MoveInDate] Product type detected:", {
        //         prodIsOffice,
        //         prodIsBoardroom,
        //     });

        //     if (prodIsOffice || prodIsBoardroom) {
        //         console.log("[MoveInDate] Running handleOfficeMoveIn()");
        //         this.handleOfficeMoveIn(dob);
        //     } else {
        //         console.log("[MoveInDate] Running handleStandardMoveIn()");
        //         this.handleStandardMoveIn(dob);
        //     }
        // },
    });
}

// async handleStandardMoveIn(dob) {
//     console.log("[handleStandardMoveIn] dob:", dob);
//     const moveOut = document.querySelector("#MoveOutDate")?.value;

//     if (moveOut) {
//         console.log("[handleStandardMoveIn] Clearing existing move out date.");
//         document.querySelector("#flexible_move_out_date")?.checked = false;
//         document.querySelector("#flexible_note")?.classList.add("d-none");
//         document.querySelector("#no_flexible_move_out_date")?.checked = false;
//         document.querySelector("#specific_move")?.classList.add("d-none");
//         document.querySelector("#specific_one_month")?.classList.add("d-none");
//         document.querySelector(".o_website_move_out_picker")?.classList.add("d-none");
//         document.querySelector("#MoveOutDate").value = "";
//     }

//     const moveDay = new Date(dob);
//     console.log("[handleStandardMoveIn] moveDay:", moveDay);

//     let rawInput1;
//     if (moveDay.getUTCDate() === 31) {
//         rawInput1 = new Date(moveDay.getFullYear(), moveDay.getMonth() + 1, 0);
//     } else if (moveDay.getUTCDate() + 1 >= 20) {
//         const nextMonth = new Date(moveDay.setMonth(moveDay.getMonth() + 1, 1));
//         rawInput1 = new Date(nextMonth.getFullYear(), nextMonth.getMonth() + 1, 0);
//     } else {
//         rawInput1 = new Date(moveDay.getFullYear(), moveDay.getMonth() + 1, 0);
//     }

//     console.log("[handleStandardMoveIn] Calculated rawInput1 (end date):", rawInput1);

//     $('input[name="renting_dates"]').daterangepicker({
//         startDate: dob,
//         endDate: rawInput1,
//     });
//     console.log("[handleStandardMoveIn] daterangepicker initialized.");

//     const prd_id = document.querySelector(".product_id")?.value;
//     console.log("[handleStandardMoveIn] Product ID:", prd_id);

//     try {
//         const result = await rpc("/bluespace/datevalidation", { dates: dob, prd_id });
//         console.log("[handleStandardMoveIn] RPC /datevalidation result:", result);
//         $("#display").html(result.msg || "");
//     } catch (err) {
//         console.error("[handleStandardMoveIn] RPC error:", err);
//     }
// }

// async handleOfficeMoveIn(dob) {
//     console.log("[handleOfficeMoveIn] dob:", dob);

//     const moveDay = new Date(dob);
//     const start_hours = parseInt($("#start_hours").val() || 7);
//     const start_minits = parseInt($("#start_minits").val() || 30);
//     const end_hours = parseInt($("#end_hours").val() || 18);
//     const end_minits = parseInt($("#end_minits").val() || 30);

//     console.log("[handleOfficeMoveIn] Time values:", {
//         start_hours,
//         start_minits,
//         end_hours,
//         end_minits,
//     });

//     function addMinutes(dt, minutes) {
//         return new Date(dt.getTime() + minutes * 60000);
//     }

//     const startDate = addMinutes(new Date(moveDay.setHours(start_hours)), start_minits);
//     const endDate = addMinutes(new Date(new Date(dob).setHours(end_hours)), end_minits);

//     console.log("[handleOfficeMoveIn] Calculated range:", { startDate, endDate });

//     $('input[name="renting_dates"]').daterangepicker({
//         startDate,
//         endDate,
//         timePicker: true,
//         timePicker24Hour: true,
//         locale: { format: "YYYY/MM/DD HH:mm" },
//     });

//     console.log("[handleOfficeMoveIn] daterangepicker initialized.");

//     try {
//         const result = await rpc("/bluespace/daysvalidation", {
//             in_date: startDate,
//             out_date: endDate,
//         });
//         console.log("[handleOfficeMoveIn] RPC /daysvalidation result:", result);
//         $("#display").html(result.msg || "");
//     } catch (err) {
//         console.error("[handleOfficeMoveIn] RPC error:", err);
//     }
// }

// // ---------------------- MOVE OUT ----------------------
initMoveOutPicker() {
    const moveOutEl = document.querySelector("#MoveOutDate");
    if (!moveOutEl) {
        console.warn("[MoveOutDate] element not found.");
        return;
    }

    console.log("[MoveOutDate] Initializing Flatpickr...");
    flatpickr(moveOutEl, {
        dateFormat: "F Y",
        minDate: "today",
        // onClose: async (selectedDates, dateStr, instance) => {
        //     console.log("[MoveOutDate] onClose fired:", selectedDates, dateStr);
        //     const moveIn = document.querySelector("#MoveInDate")?.value || "";
        //     const selected = selectedDates[0];
        //     if (!selected) {
        //         console.warn("[MoveOutDate] No date selected.");
        //         return;
        //     }

        //     console.log("[MoveOutDate] Calling /specific_one_month RPC with:", {
        //         move_in: moveIn,
        //         month_out: selected.getMonth(),
        //         year_out: selected.getFullYear(),
        //     });

        //     try {
        //         const result = await rpc("/bluespace/specific_one_month", {
        //             move_in: moveIn,
        //             month_out: selected.getMonth(),
        //             year_out: selected.getFullYear(),
        //         });

        //         console.log("[MoveOutDate] RPC /specific_one_month result:", result);
        //         $("#specific_one_month").html(result.msg || "");
        //         if (result.msg) {
        //             $("#add_to_cart").addClass("disabled");
        //             $("#specific_move").hide(200);
        //         } else {
        //             $("#add_to_cart").removeClass("disabled");
        //             $("#specific_move").show(300);
        //         }
        //     } catch (err) {
        //         console.error("[MoveOutDate] RPC error:", err);
        //     }
        // },
        // onReady: (selectedDates, dateStr, instance) => {
        //     const now = new Date();
        //     console.log("[MoveOutDate] onReady: setting default date to", now);
        //     instance.setDate(new Date(now.getFullYear(), now.getMonth(), 1));
        // },
    });
}

}

registry.category("public_components").add("move_date_picker", MoveDatePicker);
document.addEventListener("DOMContentLoaded", () => {
    console.log("[MoveDatePicker] DOMContentLoaded — starting manual initialization");
    const picker = new MoveDatePicker();
    picker.mount(document.body);
});