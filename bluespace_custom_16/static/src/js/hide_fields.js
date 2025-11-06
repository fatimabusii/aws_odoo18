/** @odoo-module **/
import PublicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";



console.log("Initializing Move-Out Fields Widget");

$(document).ready(function () {
    console.log("DOM ready, attaching MoveOutFieldsWidget");

    

    new (PublicWidget.Widget.extend({
        selector: "#wrapwrap",

        start: function () {
            console.log("MoveOutFieldsWidget start() running");

            $(".o_website_move_out_picker").hide();
            $(".label_move_out_date").hide();
            $("#flexible_note").hide();
            $("#specific_move").hide();
            $("#specific_one_month").hide();

            console.log("Move-out fields hidden successfully");

            const widget = this;

            // Flexible Lease / 1 calendar month notice
            $('input[name=is_move_out_date]').on("click", function () {
                const moveInDate = document.querySelector('.move_in_date').value;
                const date1 = new Date(moveInDate);
                const date2 = new Date();
                const days_difference = (date1.getTime() - date2.getTime()) / (1000 * 60 * 60 * 24);
                const display_msg = document.getElementById("display").innerText;

                if ($(this).is(":checked")) {
                    $(".o_website_move_out_picker").hide(300);
                    $("#flexible_note").show(300);

                    // Uncheck "Specific Move Out Date" if checked
                    if ($("#no_flexible_move_out_date").prop("checked")) {
                        $("#no_flexible_move_out_date").prop("checked", false);
                        $("#specific_move").hide(200);
                        $("#specific_one_month").hide(200);
                    }

                    // Enable add-to-cart if conditions met
                    // if (days_difference <= 60 && !display_msg) {
                    //     $("#add_to_cart").removeClass("disabled");
                    // }
                } else {
                    $(".o_website_move_out_picker").hide(200);
                    $("#is_no_move_out_date").show(300);
                    $("#flexible_note").hide(200);
                    // $("#add_to_cart").addClass("disabled");
                }
            });

            // Specific Move Out Date checkbox
            $('input[name=is_no_move_out_date]').on("click", function () {
                const moveInDate = document.querySelector('.move_in_date').value;
                const date1 = new Date(moveInDate);
                const date2 = new Date();
                const days_difference = (date1.getTime() - date2.getTime()) / (1000 * 60 * 60 * 24);
                const display_msg = document.getElementById("display").innerText;

                if ($(this).is(":checked")) {
                    $(".o_website_move_out_picker").show(300);
                    $("#specific_move").show(300);

                    // Uncheck "Flexible Lease" if checked
                    if ($("#flexible_move_out_date").prop("checked")) {
                        $("#flexible_move_out_date").prop("checked", false);
                        $("#flexible_note").hide(200);
                    }

                    // Enable add-to-cart if conditions met
                    // if (days_difference <= 60 && !display_msg) {
                    //     $("#add_to_cart").removeClass("disabled");
                    // }
                } else {
                    $(".o_website_move_out_picker").hide(200);
                    $("#is_move_out_date").show(300);
                    $("#specific_move").hide(200);
                    // $("#add_to_cart").addClass("disabled");
                }
            });

            console.log("Move-out checkbox handlers attached");

            const moveInEl = document.querySelector("#MoveInDate");
            if (moveInEl) {
                console.log("[MoveInDate] Initializing Flatpickr...");
                flatpickr(moveInEl, {
                    dateFormat: "m/d/Y",
                    minDate: "today",
                    onClose: (selectedDates, dateStr) => {
                        console.log("[MoveInDate] onClose fired. Selected:", dateStr);
                        const dob = dateStr;
                        if (!dob) return;

                        const prodIsOffice = document.querySelector("#product_is_office")?.value;
                        const prodIsBoardroom = document.querySelector("#product_is_boardroom")?.value;

                        if (prodIsOffice || prodIsBoardroom) {
                            console.log("[MoveInDate] Calling handleOfficeMoveIn");
                            this.handleOfficeMoveIn(dob);
                        } else {
                            console.log("[MoveInDate] Calling handleStandardMoveIn");
                            this.handleStandardMoveIn(dob);
                        }
                    },
                });
            }

            const moveOutEl = document.querySelector("#MoveOutDate");
            if (!moveOutEl) {
                console.warn("[MoveOutDate] element not found.");
                return;
            }

            console.log("[MoveOutDate] Initializing Flatpickr...");
            flatpickr(moveOutEl, {
                dateFormat: "F Y",
                minDate: "today",
                onClose: async (selectedDates, dateStr, instance) => {
                    console.log("[MoveOutDate] onClose fired:", selectedDates, dateStr);
                    const moveIn = document.querySelector("#MoveInDate")?.value || "";
                    const selected = selectedDates[0];
                    if (!selected) {
                        console.warn("[MoveOutDate] No date selected.");
                        return;
                    }

                    console.log("[MoveOutDate] Calling /specific_one_month RPC with:", {
                        move_in: moveIn,
                        month_out: selected.getMonth(),
                        year_out: selected.getFullYear(),
                    });

                    try {
                        const result = await rpc("/bluespace/specific_one_month", {
                            move_in: moveIn,
                            month_out: selected.getMonth(),
                            year_out: selected.getFullYear(),
                        });

                        console.log("[MoveOutDate] RPC /specific_one_month result:", result);
                        $("#specific_one_month").html(result.msg || "");
                        if (result.msg) {
                            $("#add_to_cart").addClass("disabled");
                            $("#specific_move").hide(200);
                        } else {
                            $("#add_to_cart").removeClass("disabled");
                            $("#specific_move").show(300);
                        }
                    } catch (err) {
                        console.error("[MoveOutDate] RPC error:", err);
                    }
                },
                onReady: (selectedDates, dateStr, instance) => {
                    const now = new Date();
                    console.log("[MoveOutDate] onReady: setting default date to", now);
                    instance.setDate(new Date(now.getFullYear(), now.getMonth(), 1));
                },
            });

            $('#start_hours').change(function() {
                //alert(this.value);
                var dob = $("#MoveInDate").val();
                var start_hours=document.querySelector('#start_hours').value;
                var start_minits=document.querySelector('#start_minits').value;
                var end_hours = document.querySelector('#end_hours').value;
                var end_minits = document.querySelector('#end_minits').value;
                var rawInput1='';

                function addHours(date, hours) {
                    date.setHours(date.getHours() + hours);
                    return date;
                }
                var add_minutes =  function (dt, minutes) {
                    return new Date(dt.getTime() + minutes*60000);
                }

                if (dob)
                {
                    const move_day = new Date(dob);
                    const newDate = addHours(move_day, parseInt(start_hours));
                    var dob1=add_minutes(new Date(newDate), parseInt(start_minits));
                    const move_day1 = new Date(dob);
                    const newDate1 = addHours(move_day1, 18);
                    var rawInput1=add_minutes(new Date(newDate1), 0);
                    $('input[name="renting_dates"]').daterangepicker({
                    startDate: dob1,
                    endDate: rawInput1,
                    timePicker: true,
                    timePicker24Hour: true,
                    locale: {
                        format: 'YYYY/MM/DD HH:mm'
                    },
                    });

                    var prd_id = document.querySelector('.product_id').value;
                    rpc.query({
                    route: "/bluespace/timevalidation",
                    params: {
                        hr: start_hours,
                        mn: start_minits,
                        end_hr: end_hours,
                        end_mn: end_minits,
                        prd_id: prd_id,
                        s_dt: dob1,
                        e_dt: rawInput1
                        },
                    }).then(function (result) {
                        $("#office_display").html(' ');
                        if (result.msg) {
                        $("#office_display").html(result.msg);
                        }
                    });
                }
            });

            $('#start_minits').change(function() {
                var dob = $("#MoveInDate").val();
                var start_hours=document.querySelector('#start_hours').value;
                var start_minits=document.querySelector('#start_minits').value;
                var end_hours = document.querySelector('#end_hours').value;
                var end_minits = document.querySelector('#end_minits').value;
                var rawInput1='';

                function addHours(date, hours) {
                    date.setHours(date.getHours() + hours);
                    return date;
                }
                var add_minutes =  function (dt, minutes) {
                    return new Date(dt.getTime() + minutes*60000);
                }

                if (dob)
                {
                    const move_day = new Date(dob);
                    const newDate = addHours(move_day, parseInt(start_hours));
                    var dob1=add_minutes(new Date(newDate), parseInt(start_minits));
                    const move_day1 = new Date(dob);
                    const newDate1 = addHours(move_day1, 18);
                    var rawInput1=add_minutes(new Date(newDate1), 0);
                    $('input[name="renting_dates"]').daterangepicker({
                    startDate: dob1,
                    endDate: rawInput1,
                    timePicker: true,
                    timePicker24Hour: true,
                    locale: {
                        format: 'YYYY/MM/DD HH:mm'
                    },
                    });

                var prd_id = document.querySelector('.product_id').value;
                rpc.query({
                    route: "/bluespace/timevalidation",
                    params: {
                        hr: start_hours,
                        mn: start_minits,
                        end_hr: end_hours,
                        end_mn: end_minits,
                        prd_id: prd_id,
                        s_dt: dob1,
                        e_dt: rawInput1
                        },
                    }).then(function (result) {
                    $("#office_display").html(' ');
                    if (result.msg) {
                        $("#office_display").html(result.msg);
                    }
                });
                }
            });

            console.log("[MoveOutDateOfc] Initializing Flatpickr...");
            flatpickr(moveOutEl, {
                dateFormat: "m/d/Y",
                minDate: "today",
                onClose: (selectedDates, dateStr, instance) => {
                    console.log("[MoveOutDateOfc] onClose fired. Selected:", dateStr);
                    if (!dateStr) return;

                    // Optional: Set default date to first of current month if needed
                    const now = new Date();
                    instance.setDate(new Date(now.getFullYear(), now.getMonth(), 1));
                },
                onReady: () => {
                    console.log("[MoveOutDateOfc] Flatpickr ready.");
                },
            });

            // Listen for changes to trigger Litepicker range with time
            moveOutEl.addEventListener("change", async (ev) => {
                console.log("[MoveOutDateOfc] change event fired.");
                const dob = document.querySelector("#MoveInDate")?.value;
                if (!dob) return;

                const start_hours = parseInt(document.querySelector("#start_hours")?.value || 7);
                const start_minits = parseInt(document.querySelector("#start_minits")?.value || 30);

                const addHours = (date, hours) => {
                    const d = new Date(date);
                    d.setHours(d.getHours() + hours);
                    return d;
                };
                const addMinutes = (date, minutes) => {
                    return new Date(date.getTime() + minutes * 60000);
                };

                // Compute renting range
                const moveDay = new Date(dob);
                const startDate = addMinutes(addHours(moveDay, start_hours), start_minits);

                const moveOutDateVal = document.querySelector("#MoveOutDateOfc")?.value;
                const moveOutDate = moveOutDateVal ? new Date(moveOutDateVal) : new Date();
                const endDate = addMinutes(addHours(moveOutDate, 18), 0);

                console.log("[MoveOutDateOfc] Calculated renting range:", { startDate, endDate });

                const rentingInput = document.querySelector('input[name="renting_dates"]');
                if (!rentingInput) {
                    console.warn("[MoveOutDateOfc] renting_dates input not found.");
                    return;
                }

                // Initialize Litepicker for the range with time
                new Litepicker({
                    element: rentingInput,
                    singleMode: false,
                    startDate,
                    endDate,
                    format: "YYYY/MM/DD HH:mm",
                    autoApply: true,
                    numberOfMonths: 1,
                    numberOfColumns: 1,
                    time: true,
                    lang: "en-US",
                    setup: (picker) => {
                        picker.on("selected", (date1, date2) => {
                            console.log("[Litepicker MoveOutDateOfc selected]", date1.format("YYYY/MM/DD HH:mm"), "→", date2.format("YYYY/MM/DD HH:mm"));
                        });
                    },
                });

                // Trigger RPC for days validation
                try {
                    const result = await rpc("/bluespace/daysvalidation", {
                        in_date: startDate,
                        out_date: endDate,
                    });
                    console.log("[MoveOutDateOfc] RPC /daysvalidation result:", result);
                    document.querySelector("#display").innerHTML = result.msg || "";
                } catch (err) {
                    console.error("[MoveOutDateOfc] RPC error:", err);
                }
            });

            $('#end_hours').change(function() {
                //alert(this.value);
                var dob = $("#MoveInDate").val();
                var start_hours=document.querySelector('#start_hours').value;
                var start_minits=document.querySelector('#start_minits').value;
                var end_hours = document.querySelector('#end_hours').value;
                var end_minits = document.querySelector('#end_minits').value;
                var rawInput1='';

                function addHours(date, hours) {
                    date.setHours(date.getHours() + hours);
                    return date;
                }
                var add_minutes =  function (dt, minutes) {
                    return new Date(dt.getTime() + minutes*60000);
                }

                if (dob)
                {
                    const move_day = new Date(dob);
                    const newDate = addHours(move_day, parseInt(start_hours));
                    var dob1=add_minutes(new Date(newDate), parseInt(start_minits));
                    const move_day1 = new Date(dob);
                    const newDate1 = addHours(move_day1, parseInt(end_hours));
                    var rawInput1=add_minutes(new Date(newDate1), parseInt(end_minits));
                    $('input[name="renting_dates"]').daterangepicker({
                    startDate: dob1,
                    endDate: rawInput1,
                    timePicker: true,
                    timePicker24Hour: true,
                    locale: {
                        format: 'YYYY/MM/DD HH:mm'
                    },
                    });
                }

                var prd_id = document.querySelector('.product_id').value;
                rpc.query({
                    route: "/bluespace/timevalidation",
                    params: {
                        hr: start_hours,
                        mn: start_minits,
                        end_hr: end_hours,
                        end_mn: end_minits,
                        prd_id: prd_id,
                        s_dt: dob1,
                        e_dt: rawInput1
                        },
                    }).then(function (result) {
                    $("#office_display").html(' ');
                    if (result.msg) {
                        $("#office_display").html(result.msg);
                    }
                });
            });

            $('#end_minits').change(function() {
                var dob = $("#MoveInDate").val();
                var start_hours=document.querySelector('#start_hours').value;
                var start_minits=document.querySelector('#start_minits').value;
                var end_hours = document.querySelector('#end_hours').value;
                var end_minits = document.querySelector('#end_minits').value;
                var rawInput1='';

                function addHours(date, hours) {
                    date.setHours(date.getHours() + hours);
                    return date;
                }
                var add_minutes =  function (dt, minutes) {
                    return new Date(dt.getTime() + minutes*60000);
                }

                if (dob)
                {
                    const move_day = new Date(dob);
                    const newDate = addHours(move_day, parseInt(start_hours));
                    var dob1=add_minutes(new Date(newDate), parseInt(start_minits));
                    const move_day1 = new Date(dob);
                    const newDate1 = addHours(move_day1, parseInt(end_hours));
                    var rawInput1=add_minutes(new Date(newDate1), parseInt(end_minits));
                    $('input[name="renting_dates"]').daterangepicker({
                    startDate: dob1,
                    endDate: rawInput1,
                    timePicker: true,
                    timePicker24Hour: true,
                    locale: {
                        format: 'YYYY/MM/DD HH:mm'
                    },
                    });
                }

                var prd_id = document.querySelector('.product_id').value;
                rpc.query({
                    route: "/bluespace/timevalidation",
                    params: {
                        hr: start_hours,
                        mn: start_minits,
                        end_hr: end_hours,
                        end_mn: end_minits,
                        prd_id: prd_id,
                        s_dt: dob1,
                        e_dt: rawInput1
                        },
                    }).then(function (result) {
                    $("#office_display").html(' ');
                    if (result.msg) {
                        $("#office_display").html(result.msg);
                    }
                });
            });

            $('#OfcPerson').on('change', function (event) {
                var p1=document.querySelector('#OfcPerson').value;
                var prod_size = document.querySelector('#product_size').value;
                var prod_is_office = document.querySelector('#product_is_office').value;
                var prod_is_boardroom = document.querySelector('#product_is_boardroom').value;
                $("#person_display").html(' ');
                if (prod_is_office) {
                if (prod_size == 16 && p1 > 4)
                {
                    $("#person_display").html('Please note, this office can only accommodate a maximum of 4 people.');
                }
                if (prod_size == 17 && p1 > 6)
                {
                    $("#person_display").html('Please note, this office can only accommodate a maximum of 6 people.');
                }
                if (prod_size == 20 && p1 > 8)
                {
                    $("#person_display").html('Please note, this office can only accommodate a maximum of 8 people.');
                }
                if (prod_size == 41 && p1 > 17)
                {
                    $("#person_display").html('Please note, this office can only accommodate a maximum of 17 people.');
                }
                }

                if (prod_is_boardroom) {
                if (prod_size == 16 && p1 > 6)
                {
                    $("#person_display").html('Please note, this boardroom can only accommodate a maximum of 6 people.');
                }
                if (prod_size == 19 && p1 > 10)
                {
                    $("#person_display").html('Please note, this boardroom can only accommodate a maximum of 10 people.');
                }
                }
            });

            var url = window.location.pathname;
            if (url == '/shop/create_account') {
                var entity_rep = document.getElementById("legal_entity").value;

                rpc.query({
                    route: "/bluespace/legal_entity",
                    params: {
                        entity_id : entity_rep
                        },
                    }).then(function (result) {
                    if (result) {
                        $("#entity_representative").hide();
                        $("#individual_entity").show();
                    } else {
                        $("#entity_representative").show();
                        $("#individual_entity").hide();
                    }
                });

                $('#legal_entity').on('change', function (e) {
                var optionSelected = $("option:selected", this);
                var valueSelected = this.value;
                rpc.query({
                    route: "/bluespace/legal_entity",
                    params: {
                        entity_id : this.value
                        },
                    }).then(function (result) {
                    if (result) {
                        $("#entity_representative").hide();
                        $("#individual_entity").show();
                    } else {
                        $("#entity_representative").show();
                        $("#individual_entity").hide();
                    }
                });
                });
            }
        },

        // --------------------------------------------
        // Define your async methods here
        // --------------------------------------------
        handleStandardMoveIn: async function (dob) {
            console.log("[handleStandardMoveIn] dob:", dob);
            const moveOut = document.querySelector("#MoveOutDate")?.value;

            if (moveOut) {
                console.log("[handleStandardMoveIn] Clearing existing move out date.");
     
                const flexibleMoveOut = document.querySelector("#flexible_move_out_date");
                if (flexibleMoveOut) flexibleMoveOut.checked = false;

                const noFlexibleMoveOut = document.querySelector("#no_flexible_move_out_date");
                if (noFlexibleMoveOut) noFlexibleMoveOut.checked = false;

                const specificMove = document.querySelector("#specific_move");
                if (specificMove) specificMove.classList.add("d-none");

                const specificOneMonth = document.querySelector("#specific_one_month");
                if (specificOneMonth) specificOneMonth.classList.add("d-none");

                const moveOutPicker = document.querySelector(".o_website_move_out_picker");
                if (moveOutPicker) moveOutPicker.classList.add("d-none");

                const moveOutDate = document.querySelector("#MoveOutDate");
                if (moveOutDate) moveOutDate.value = "";

            }

            const moveDay = new Date(dob);
            let rawInput1;
            if (moveDay.getUTCDate() === 31) {
                rawInput1 = new Date(moveDay.getFullYear(), moveDay.getMonth() + 1, 0);
            } 
            else if (moveDay.getUTCDate() + 1 >= 20) {
                const nextMonth = new Date(moveDay.setMonth(moveDay.getMonth() + 1, 1));
                rawInput1 = new Date(nextMonth.getFullYear(), nextMonth.getMonth() + 1, 0);
            } 
            else {
                rawInput1 = new Date(moveDay.getFullYear(), moveDay.getMonth() + 1, 0);
            }
            
            
            console.log("[handleStandardMoveIn] Initializing Litepicker from", dob, "to", rawInput1);

            const rentingInput = document.querySelector('input[name="renting_dates"]');
            if (!rentingInput) {
                console.warn("[handleStandardMoveIn] renting_dates input not found.");
                return;
            }

            new Litepicker({
                element: rentingInput,
                singleMode: false, // range mode
                startDate: dob,
                endDate: rawInput1,
                format: "YYYY-MM-DD",
                autoApply: true,
                numberOfMonths: 2,
                numberOfColumns: 2,
                setup: (picker) => {
                    picker.on('selected', (date1, date2) => {
                        console.log("[Litepicker selected] Range:", date1.format('YYYY-MM-DD'), "→", date2.format('YYYY-MM-DD'));
                    });
                }
            });

            console.log("[handleStandardMoveIn] Litepicker initialized successfully.");

            const prd_id = document.querySelector(".product_id")?.value;
            try {
                const result = await rpc("/bluespace/datevalidation", { dates: dob, prd_id });
                console.log("[handleStandardMoveIn] RPC result:", result);
                $("#display").html(result.msg || "");
            } catch (err) {
                console.error("[handleStandardMoveIn] RPC error:", err);
            }
        },

        handleOfficeMoveIn: async function (dob) {
            console.log("[handleOfficeMoveIn] dob:", dob);

            const moveDay = new Date(dob);
            const start_hours = parseInt($("#start_hours").val() || 7);
            const start_minits = parseInt($("#start_minits").val() || 30);
            const end_hours = parseInt($("#end_hours").val() || 18);
            const end_minits = parseInt($("#end_minits").val() || 30);

            function addMinutes(dt, minutes) {
                return new Date(dt.getTime() + minutes * 60000);
            }

            const startDate = addMinutes(new Date(moveDay.setHours(start_hours)), start_minits);
            const endDate = addMinutes(new Date(new Date(dob).setHours(end_hours)), end_minits);

            console.log("[handleOfficeMoveIn] Calculated range:", { startDate, endDate });

            const rentingInput = document.querySelector('input[name="renting_dates"]');
            if (!rentingInput) {
                console.warn("[handleOfficeMoveIn] renting_dates input not found.");
                return;
            }

            // Initialize Litepicker with time picker enabled
            new Litepicker({
                element: rentingInput,
                singleMode: false, // enable range mode
                startDate: startDate,
                endDate: endDate,
                format: "YYYY/MM/DD HH:mm",
                autoApply: true,
                numberOfMonths: 1,
                numberOfColumns: 1,
                showTooltip: true,
                tooltipText: { one: "day", other: "days" },
                tooltipNumber: (totalDays) => totalDays - 1,
                time: true, // enables time selection
                lang: "en-US",
                setup: (picker) => {
                    picker.on("selected", (date1, date2) => {
                        console.log("[Litepicker selected] Range:", date1.format("YYYY/MM/DD HH:mm"), "→", date2.format("YYYY/MM/DD HH:mm"));
                    });
                },
            });

            console.log("[handleOfficeMoveIn] Litepicker with time initialized successfully.");


            try {
                const result = await rpc("/bluespace/daysvalidation", { in_date: startDate, out_date: endDate });
                console.log("[handleOfficeMoveIn] RPC result:", result);
                $("#display").html(result.msg || "");
            } catch (err) {
                console.error("[handleOfficeMoveIn] RPC error:", err);
            }
        },
    }))().attachTo($("#wrapwrap"));
    
});


