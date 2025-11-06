/** @odoo-module **/

// // import { WebsiteSale } from 'website_sale.website_sale';
// import { WebsiteSale } from '@website_sale/js/website_sale';
// import { RentingMixin } from '@website_sale_renting/js/renting_mixin';
// import '@website_sale_renting/js/variant_mixin';
// import { _t } from '@web/core/l10n/translation';
// import { sprintf } from "@web/core/utils/strings";
// import { deserializeDateTime, momentToLuxon, serializeDateTime } from "@web/core/l10n/dates";

// export const msecPerUnit = {
//     hour: 3600 * 1000,
//     day: 3600 * 1000 * 24,
//     week: 3600 * 1000 * 24 * 7,
//     month: 3600 * 1000 * 24 * 30,
// };
// export const unitMessages = {
//     hour: _t("(%s hours)."),
//     day: _t("(%s days)."),
//     week: _t("(%s weeks)."),
//     month: _t("(%s months)."),
// };

// WebsiteSale.include(RentingMixin);
// WebsiteSale.include({
    
//     _getRentingDates($product) {
//         this._super(...arguments);
//         console.log("TESTTTTTT")
//         const rentingDates = ($product || this.$el).find('input[name=renting_dates]');
//         var is_move_out_date_data="";
//         var rawInput1='';
//         var rawInput='';
//         const monthsLong = {
//               January: '01',
//               February: '02',
//               March: '03',
//               April: '04',
//               May: '05',
//               June: '06',
//               July: '07',
//               August: '08',
//               September: '09',
//               October: '10',
//               November: '11',
//               December: '12',
//             };

//         var prod_is_office = document.querySelector('#product_is_office').value || document.querySelector('#product_is_boardroom').value;
//         if (prod_is_office) {
//             var rawInput = '';
//             var rawInput1 = '';
//             if (document.querySelector('.move_in_date').value)
//             {
//                 var move_in_date = document.querySelector('.move_in_date').value;
//                 var start_hours = document.querySelector('#start_hours').value;
//                 var start_minits = document.querySelector('#start_minits').value;
//                 var move_out_date = document.querySelector('.move_out_date_ofc').value;
//                 var end_hours = document.querySelector('#end_hours').value;
//                 var end_minits = document.querySelector('#end_minits').value;

//                 function addHours(date, hours) {
//                     date.setHours(date.getHours() + hours);
//                     return date;
//                 }
//                 var add_minutes =  function (dt, minutes) {
//                       return new Date(dt.getTime() + minutes*60000);
//                 }
//                 //start_hours = parseInt(start_hours) ? start_hours : 7;
//                 //start_minits = parseInt(start_minits) ? start_minits : 30;

//                 const move_day = new Date(move_in_date);
//                 const newDate = addHours(move_day, parseInt(start_hours));
//                 rawInput=add_minutes(new Date(newDate), parseInt(start_minits));

//                 if (move_out_date)
//                 {
//                     const move_day1 = new Date(move_out_date);
//                     const newDate1 = addHours(move_day1, end_hours);
//                     rawInput1=add_minutes(new Date(newDate1), end_minits);
//                 }
//                 else
//                 {
//                     const move_day1 = new Date(move_in_date);
//                     const newDate1 = addHours(move_day1, 18);
//                     rawInput1=add_minutes(new Date(newDate1), 0);
//                 }
//             }
//         }
//         else
//         {
//             if (document.querySelector('.flexible_move_out_date').checked==true){
//                 rawInput=document.querySelector('.move_in_date').value;

//                 var move_dt=document.querySelector('.move_out_date').value
//                 const myArray = move_dt.split(" ");
//                 var month_number=monthsLong[myArray[0]]
//                 var lastDay = new Date(parseInt(myArray[1]), parseInt(month_number), 0).getDate();
//                 var month_last=month_number+'/'+lastDay+'/'+parseInt(myArray[1])
//                 var myDate = new Date(month_last);
//                 rawInput1=myDate;
//             }
//             else
//             {
//                 if (document.querySelector('.move_in_date').value)
//                     var rawInput = document.querySelector('.move_in_date').value;
//                 const move_day = new Date(rawInput);

//                 if (move_day.getUTCDate() == 31)
//                 {
//                     var lastDay = new Date(move_day.getFullYear(), move_day.getMonth()+ 1, 0)
//                     rawInput1 = lastDay;
//                 }
//                 else if (move_day.getUTCDate()+1 >= 20)
//                 {
//                     var n=move_day.setMonth(move_day.getMonth()+1,1);
//                     var dt = new Date(n);
//                     var lastDay = new Date(dt.getFullYear(), dt.getMonth() + 1, 0)
//                     rawInput1 = lastDay;
//                 }
//                 else
//                 {
//                     var lastDay = new Date(move_day.getFullYear(), move_day.getMonth()+ 1, 0)
//                     rawInput1 = lastDay;
//                 }
//             }
//         }
//         if (rawInput) {
//             const picker = rentingDates.data('daterangepicker');
//             const a = this._getDateFromInputOrDefault(picker, 'startDate', 'start_date');
//             const b = this._getDateFromInputOrDefault(picker, 'endDate', 'end_date');

//             var move_in_luxonDate = moment(rawInput);
//             var mvi_dt_momentToLuxon = momentToLuxon(move_in_luxonDate);
//             var move_out_luxonDate = moment(rawInput1);
//             var mvo_dt_momentToLuxon = momentToLuxon(move_out_luxonDate);

//             return {
//                 start_date: mvi_dt_momentToLuxon,
//                 end_date: mvo_dt_momentToLuxon,
                
//             };
//         }
//         return {};
//     },
    
//     _onChangeCombination: function (ev, $parent, combination) {
//         var prod_is_office = document.querySelector('#product_is_office').value || document.querySelector('#product_is_boardroom').value;
//         if (prod_is_office) {
//             var move_in_hours = document.querySelector('#start_hours').value;
//             var move_in_minutes = document.querySelector('#start_minits').value;
//             var move_out_hours = document.querySelector('#end_hours').value;
//             var move_out_minutes = document.querySelector('#end_minits').value;
//             var move_in_date=document.querySelector('.move_in_date').value;
//             var move_Out_dt=document.querySelector('.move_out_date_ofc').value;
//             var no_of_person=document.querySelector('#OfcPerson').value;
//             var prod_size = document.querySelector('#product_size').value;
//             if (combination.is_rental) {
//                 const $rentingDetails = $parent.find(".o_renting_details");
//                 const $rentalduration = $rentingDetails.find(".o_renting_duration_rantal");
//                 $rentalduration.text(combination.month_days);
//                 const $freeOfficeMsg = $rentingDetails.find(".o_free_office_msg");
//                 $freeOfficeMsg.text(combination.free_office_msg);
//             }
//             this._super.apply(this, arguments);

//             var flag = false;
//             if (move_Out_dt)
//             {
//                 const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
//                 var diffDays = Math.round(Math.abs((new Date(move_in_date) - new Date(move_Out_dt)) / oneDay));
//                 var msg1 = document.getElementById("office_display").innerText;
//                 var display_msg = document.getElementById("display").innerText;
//                 var mv_in_hr = parseInt(move_in_hours);
//                 var mv_in_mn = parseInt(move_in_minutes);
//                 var mv_out_hr = parseInt(move_out_hours);
//                 var mv_out_mn = parseInt(move_out_minutes);

//                 var dt1 = new Date(move_in_date);
//                 var dt2 = new Date(move_Out_dt);
//                 var weekend_cnt = 0;

//                 while (dt1 < dt2) {
//                     var day = dt1.getDay();
//                     if ((day === 6) || (day === 0)) {
//                         weekend_cnt++ ;
//                     }
//                     dt1.setDate(dt1.getDate() + 1);
//                 }
//                 diffDays = diffDays - weekend_cnt;

//                 //if ((move_in_hours >= 7 &&  move_in_minutes >= 30 && move_out_hours <= 18 && move_out_minutes >= 30) && diffDays < 6)
//                 if ((((mv_in_hr >= 7 &&  mv_in_mn >= 30) || (mv_in_hr > 7 &&  mv_in_mn >= 0)) && ((mv_out_hr < 18 && mv_out_mn >= 0) || (mv_out_hr == 18 && mv_out_mn == 0))) && diffDays < 6 && (!display_msg && !msg1))
//                 {
//                     flag = true;
//                 }
//             }
//             this._toggleDisable($parent, flag);
//         }
//         else
//         {
//             var move_in = document.querySelector('#flexible_move_out_date').checked;
//             var move_out = document.querySelector('#no_flexible_move_out_date').checked;
//             var move_in_date=document.querySelector('.move_in_date').value;
//             const date1 = new Date(move_in_date);
//             const date2 = new Date();
//             var days_difference = (date1.getTime() - date2.getTime()) / (1000 * 60 * 60 * 24);
//             var display_msg = document.getElementById("display").innerText;

//             if (combination.is_rental) {
//                 const $rentingDetails = $parent.find(".o_renting_details");
//                 const $rentalduration = $rentingDetails.find(".o_renting_duration_rantal");
//                 $rentalduration.text(combination.month_days);
//                 const $freeOfficeMsg = $rentingDetails.find(".o_free_office_msg");
//                 $freeOfficeMsg.text(combination.free_office_msg);
//             }
//             this._super.apply(this, arguments);
//             var move_in1 = false

//             if ((move_in || move_out) && days_difference <= 60 && !display_msg){
//                 move_in1 = move_in || move_out
//             }
//             this._toggleDisable($parent, move_in1);
//         }
//     },

// });

import { WebsiteSale } from '@website_sale/js/website_sale';
import { RentingMixin } from '@website_sale_renting/js/renting_mixin';
import '@website_sale_renting/js/variant_mixin';
import { _t } from '@web/core/l10n/translation';
import { momentToLuxon } from '@web/core/l10n/dates';
import { rpc } from "@web/core/network/rpc"

export const msecPerUnit = {
    hour: 3600 * 1000,
    day: 3600 * 1000 * 24,
    week: 3600 * 1000 * 24 * 7,
    month: 3600 * 1000 * 24 * 30,
};

export const unitMessages = {
    hour: _t("(%s hours)."),
    day: _t("(%s days)."),
    week: _t("(%s weeks)."),
    month: _t("(%s months)."),
};

WebsiteSale.include(RentingMixin);

export class CustomWebsiteSale extends WebsiteSale {
    _getRentingDates($product) {
        const rentingDates = ($product || this.$el).find('input[name=renting_dates]');
        let rawInput = '';
        let rawInput1 = '';
        const monthsLong = {
            January: '01', February: '02', March: '03', April: '04',
            May: '05', June: '06', July: '07', August: '08',
            September: '09', October: '10', November: '11', December: '12',
        };

        const prod_is_office = document.querySelector('#product_is_office')?.value || document.querySelector('#product_is_boardroom')?.value;
        
        if (prod_is_office) {
            const move_in_date = document.querySelector('.move_in_date')?.value;
            const move_out_date = document.querySelector('.move_out_date_ofc')?.value;
            if (move_in_date) {
                const start_hours = parseInt(document.querySelector('#start_hours')?.value) || 0;
                const start_minutes = parseInt(document.querySelector('#start_minits')?.value) || 0;
                const end_hours = parseInt(document.querySelector('#end_hours')?.value) || 18;
                const end_minutes = parseInt(document.querySelector('#end_minits')?.value) || 0;

                const addHours = (date, hours) => { date.setHours(date.getHours() + hours); return date; };
                const addMinutes = (date, minutes) => new Date(date.getTime() + minutes * 60000);

                const moveDay = new Date(move_in_date);
                rawInput = addMinutes(addHours(new Date(moveDay), start_hours), start_minutes);

                if (move_out_date) {
                    const moveDayOut = new Date(move_out_date);
                    rawInput1 = addMinutes(addHours(new Date(moveDayOut), end_hours), end_minutes);
                } else {
                    rawInput1 = addMinutes(addHours(new Date(move_in_date), 18), 0);
                }
            }
        } else {
            if (document.querySelector('.flexible_move_out_date')?.checked) {
                rawInput = document.querySelector('.move_in_date')?.value;
                const move_dt = document.querySelector('.move_out_date')?.value;
                const myArray = move_dt.split(" ");
                const month_number = monthsLong[myArray[0]];
                const lastDay = new Date(parseInt(myArray[1]), parseInt(month_number), 0).getDate();
                rawInput1 = new Date(`${month_number}/${lastDay}/${parseInt(myArray[1])}`);
            } else {
                rawInput = document.querySelector('.move_in_date')?.value;
                const move_day = new Date(rawInput);
                let lastDay;
                if (move_day.getUTCDate() === 31) {
                    lastDay = new Date(move_day.getFullYear(), move_day.getMonth() + 1, 0);
                } else if (move_day.getUTCDate() + 1 >= 20) {
                    const dt = new Date(move_day.setMonth(move_day.getMonth() + 1, 1));
                    lastDay = new Date(dt.getFullYear(), dt.getMonth() + 1, 0);
                } else {
                    lastDay = new Date(move_day.getFullYear(), move_day.getMonth() + 1, 0);
                }
                rawInput1 = lastDay;
            }
        }

        if (rawInput) {
            const move_in_luxonDate = momentToLuxon(rawInput);
            const move_out_luxonDate = momentToLuxon(rawInput1);
            return { start_date: move_in_luxonDate, end_date: move_out_luxonDate };
        }
        return {};
    }

    _onChangeCombination(ev, $parent, combination) {
        const prod_is_office = document.querySelector('#product_is_office')?.value || document.querySelector('#product_is_boardroom')?.value;
        if (combination.is_rental) {
            const $rentingDetails = $parent.find(".o_renting_details");
            $rentingDetails.find(".o_renting_duration_rantal").text(combination.month_days);
            $rentingDetails.find(".o_free_office_msg").text(combination.free_office_msg);
        }

        super._onChangeCombination(ev, $parent, combination);

        let flag = false;
        if (prod_is_office) {
            const move_in_date = document.querySelector('.move_in_date')?.value;
            const move_out_date = document.querySelector('.move_out_date_ofc')?.value;
            if (move_in_date && move_out_date) {
                const oneDay = 24 * 60 * 60 * 1000;
                const diffDays = Math.round(Math.abs((new Date(move_in_date) - new Date(move_out_date)) / oneDay));
                flag = diffDays < 6;
            }
            this._toggleDisable($parent, flag);
        } else {
            const move_in_checked = document.querySelector('#flexible_move_out_date')?.checked;
            const move_out_checked = document.querySelector('#no_flexible_move_out_date')?.checked;
            const move_in_date = document.querySelector('.move_in_date')?.value;
            const days_difference = (new Date(move_in_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24);
            this._toggleDisable($parent, (move_in_checked || move_out_checked) && days_difference <= 60 && !document.getElementById("display")?.innerText);
        }
    }
}

// MoveOut handler logic safely
document.querySelectorAll(".o_website_move_out_picker, .label_move_out_date, #flexible_note, #specific_move")
    .forEach(el => { if (el) el.style.display = 'none'; });

const moveOutHandler = (selector, showFlex, hideFlex, showSpecific, hideSpecific) => {
    document.querySelectorAll(`input[name="${selector}"]`).forEach(input => {
        input.addEventListener('click', () => {
            const showFlexEl = document.querySelector(showFlex);
            const hideFlexEl = document.querySelector(hideFlex);
            const showSpecificEl = document.querySelector(showSpecific);
            const hideSpecificEl = document.querySelector(hideSpecific);

            if (input.checked) {
                if (showFlexEl) showFlexEl.style.display = 'block';
                if (hideFlexEl) hideFlexEl.style.display = 'none';
                if (showSpecificEl) showSpecificEl.style.display = 'block';
                if (hideSpecificEl) hideSpecificEl.style.display = 'none';
            } else {
                if (showFlexEl) showFlexEl.style.display = 'none';
                if (showSpecificEl) showSpecificEl.style.display = 'none';
            }
        });
    });
};

moveOutHandler('is_move_out_date', '#flexible_note', '#is_no_move_out_date', '#specific_move', '#specific_one_month');
moveOutHandler('is_no_move_out_date', '#specific_move', '#flexible_note', '#flexible_note', '#specific_one_month');

const moveOutDateInput = document.getElementById('MoveOutDate');
if (moveOutDateInput) {
    flatpickr(moveOutDateInput, {
        dateFormat: "m/d/Y",
        onChange(selectedDates, dateStr) {
            rpc.query({
                route: "/bluespace/MoveOutDate",
                params: { dates: dateStr },
            }).then(result => {
                const displayEl = document.getElementById("display");
                if (displayEl) displayEl.innerHTML = result.msg || '';
            });
        }
    });
}
