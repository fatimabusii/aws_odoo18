
odoo.define('bluespace_custom_16.date_validation', function (require) {
'use strict';

  require('web.dom_ready');
  var rpc = require('web.rpc');

  $("#warehouse").on('click', function () {
      $('#warehouse_box').modal('show');
      $("#products_grid").css("z-index", -1);
  });
  $("#warehouse_close").on('click', function () {
      $('#warehouse_box').modal('hide');
      $("#products_grid").css("z-index", 1);
  });

  $("#office").on('click', function () {
      $('#office_box').modal('show');
      $("#products_grid").css("z-index", -1);
  });
  $("#office_close").on('click', function () {
      $('#office_box').modal('hide');
      $("#products_grid").css("z-index", 1);
  });
  $("#vehicle").on('click', function () {
      $('#vehicle_box').modal('show');
      $("#products_grid").css("z-index", -1);
  });
  $("#vehicle_close").on('click', function () {
      $('#vehicle_box').modal('hide');
      $("#products_grid").css("z-index", 1);
  });
  $("#boardroom").on('click', function () {
      $('#boardroom_box').modal('show');
      $("#products_grid").css("z-index", -1);
  });
  $("#boardroom_close").on('click', function () {
      $('#boardroom_box').modal('hide');
      $("#products_grid").css("z-index", 1);
  });

  $("#warehouse_summary").on('click', function () {
    console.log("nnnnnnnnnnnn")
      $('#warehouse_box_suumery').modal('show');
      $("#products_grid").css("z-index", -1);
  });
  $("#warehouse_summeryclose").on('click', function () {
      $('#warehouse_box_suumery').modal('hide');
      $("#products_grid").css("z-index", 1);
  });

  $(".o_website_move_out_picker").hide();
  $(".label_move_out_date").hide();
  $("#flexible_note").hide();
  $("#specific_move").hide();

  $('input[name=is_move_out_date]').click(function() {
      
      if($(this).is(":checked")) {
          $(".o_website_move_out_picker").hide(300);
          //$(".label_move_out_date").hide(300);
          //$("#is_no_move_out_date").hide(300);
          $("#flexible_note").show(300);
          //$("#add_to_cart").removeClass('disabled');
          var move_in_date=document.querySelector('.move_in_date').value;
          const date1 = new Date(move_in_date);
          const date2 = new Date();
          var days_difference = (date1.getTime() - date2.getTime()) / (1000 * 60 * 60 * 24);
          var display_msg = document.getElementById("display").innerText;

          if ( days_difference <= 60 && !display_msg) {
            $("#add_to_cart").removeClass('disabled');
          }

          var specific_checkbox = document.getElementById("no_flexible_move_out_date").checked;
          if (specific_checkbox) {
            document.getElementById("no_flexible_move_out_date").checked = false;
            $("#specific_move").hide(200);
            $("#specific_one_month").hide(200);
          }
      } else {
          $(".o_website_move_out_picker").hide(200);
          $(".label_move_out_date").hide(200);
          $("#is_no_move_out_date").show(300);
          $("#flexible_note").hide(200);
          $("#add_to_cart").addClass('disabled');
      }
  });
  $('input[name=is_no_move_out_date]').click(function() {
      if($(this).is(":checked")) {
          $(".o_website_move_out_picker").show(300);
          //$(".label_move_out_date").show(300);
          //$("#is_move_out_date").hide(300);
          $("#specific_move").show(300);
          //$("#add_to_cart").removeClass('disabled');
          var move_in_date=document.querySelector('.move_in_date').value;
          const date1 = new Date(move_in_date);
          const date2 = new Date();
          var days_difference = (date1.getTime() - date2.getTime()) / (1000 * 60 * 60 * 24);
          var display_msg = document.getElementById("display").innerText;

          if ( days_difference <= 60 && !display_msg) {
            $("#add_to_cart").removeClass('disabled');
          }

          var m2m_checkbox = document.getElementById("flexible_move_out_date").checked;
          if (m2m_checkbox) {
            document.getElementById("flexible_move_out_date").checked = false;
            $("#flexible_note").hide(200);
          }
      } else {
          $(".o_website_move_out_picker").hide(200);
          $(".label_move_out_date").hide(200);
          $("#is_move_out_date").show(300);
          $("#specific_move").hide(200);
          $("#add_to_cart").addClass('disabled');
      }
  });
  
  $('#MoveOutDate').datepicker({
     changeMonth: true,
     changeYear: true,
     dateFormat: 'MM yy',
     minDate: 0,
     showButtonPanel: true,       

    onClose: function(dateText, inst) {
        var move_in = $("#MoveInDate").val();
        rpc.query({
          route: "/bluespace/specific_one_month",
          params: {
              move_in: move_in,
              month_out: inst.selectedMonth,
              year_out: inst.selectedYear},
          }).then(function (result) {
            $("#specific_one_month").html(' ');
            if (result.msg) {
              $("#specific_one_month").html(result.msg);
              $("#add_to_cart").addClass('disabled');
              $("#specific_move").hide(200);
            }
            else {
              $("#add_to_cart").removeClass('disabled');
              $("#specific_move").show(300);
            }
        });
        var iMonth = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
        var iYear = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
        $(this).datepicker('setDate', new Date(inst.selectedYear, inst.selectedMonth, 1));
     },
     beforeShow: function() {
      var dob = $("#MoveOutDate").val();
      var selDate = $(this).val().length > 0
       if (dob) 
       {
          var iYear = new Date().getFullYear();
          var iMonth = new Date().getMonth();
          $(this).datepicker('option', 'defaultDate', new Date(iYear, iMonth, 1));
          $(this).datepicker('setDate', new Date(iYear, iMonth, 1));
       }
    }   
  });

  $("#MoveOutDate").on("change.datepicker", ({date}) => {
      var dob = $("#MoveOutDate").val();
      rpc.query({
        route: "/bluespace/MoveOutDate",
        params: {
            dates: dob},
        }).then(function (result) {
          $("#display").html(' ');
          if (result.msg) {
            $("#display").html(result.msg);
          }
      });
      
    });

  $(".move_out_date").click(function () {
        $(".ui-datepicker-calendar").hide();
        console.log("dob>>>>>>click>>>>>>>>>>>>>>");
        $("#ui-datepicker-div").position({
            my: "center top",
            at: "center bottom",
            of: $(this)
        });
    });

  $(".move_out_date").focus(function () {
        $(".ui-datepicker-calendar").hide();
        $("#ui-datepicker-div").position({
            my: "center top",
            at: "center bottom",
            of: $(this)
        });
    });

  $('#MoveInDate').datepicker({
     changeMonth: true,
     changeYear: true,
     dateFormat: 'mm/dd/yy',
     minDate: 0,
     /*beforeShowDay: $.datepicker.noWeekends,*/

     onClose: function() {
        var iMonth = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
        var iYear = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
        var selDate=$(this).datepicker(new Date(iYear, iMonth, 1));
        
     },
     beforeShow: function() {
      var dob = $("#MoveInDate").val();
      var selDate = $(this).val().length > 0
       if (dob) 
       {
          var iYear = new Date().getFullYear();
          var iMonth = new Date().getMonth();
          $(this).datepicker('option', 'defaultDate', new Date(iYear, iMonth, 1));
          /*$(this).datepicker('setDate', new Date(iYear, iMonth, 1));*/
       }
       else {
          $(this).datepicker('setDate', new Date());
       }
    }  
  });

  $("#MoveInDate").on("change.datepicker", ({date}) => {
      var dob = $("#MoveInDate").val();
      var rawInput1='';

      var prod_is_office = document.querySelector('#product_is_office').value || document.querySelector('#product_is_boardroom').value;
      if (prod_is_office)
      {
        if (dob)
        {
          var rawInput=new Date(dob);
          var rawInput1='';
          const move_day = new Date(dob);
          var start_hours = document.querySelector('#start_hours').value;
          var start_minits = document.querySelector('#start_minits').value;
          var move_out_date = document.querySelector('.move_out_date_ofc').value;
          var end_hours = document.querySelector('#end_hours').value;
          var end_minits = document.querySelector('#end_minits').value;

          function addHours(date, hours) {
              date.setHours(date.getHours() + hours);
              return date;
          }
          var add_minutes =  function (dt, minutes) {
                return new Date(dt.getTime() + minutes*60000);
          }
          $('#start_hours option:eq(7)').attr('selected', true);
          if ('#start_minits option:eq(30)')
          {
            $('#start_minits option:eq(30)').attr('selected', true);
          }

          document.querySelector('.move_out_date_ofc').value = dob;
          $('#end_hours option:eq(18)').attr('selected', true);
          $('#end_minits option:eq(30)').attr('selected', true);

          start_hours = parseInt(start_hours) ? start_hours : 7;
          start_minits = parseInt(start_minits) ? start_minits : 30;

          const newDate = addHours(move_day, parseInt(start_hours));
          rawInput=add_minutes(new Date(newDate), parseInt(start_minits));

          const move_day1 = new Date(dob);
          const newDate1 = addHours(move_day1, parseInt(end_hours));
          rawInput1=add_minutes(new Date(newDate1), parseInt(end_minits));

          $('input[name="renting_dates"]').daterangepicker({
            startDate: rawInput,
            endDate: rawInput1,
            timePicker: true,
            timePicker24Hour: true,
            locale: {
              format: 'YYYY/MM/DD HH:mm'
            },
          });

          rpc.query({
            route: "/bluespace/daysvalidation",
            params: {
                in_date: rawInput,
                out_date: rawInput1
              },
            }).then(function (result) {
              $("#display").html(' ');
              if (result.msg) {
                $("#display").html(result.msg);
              }
          });
        }
      }
      else {
        if (dob)
        {
          var move_out = $("#MoveOutDate").val();
          if (move_out)
          {
            document.getElementById("flexible_move_out_date").checked = false;
            $("#flexible_note").hide(200);
            document.getElementById("no_flexible_move_out_date").checked = false;
            $("#specific_move").hide(200);
            $("#specific_one_month").hide(200);
            $(".o_website_move_out_picker").hide(200);
            document.querySelector('#MoveOutDate').value = "";
          }
          const move_day = new Date(dob);
          if (move_day.getUTCDate() == 31)
              {
                  var lastDay = new Date(move_day.getFullYear(), move_day.getMonth()+ 1, 0)
                  rawInput1 = lastDay;
              }
              else if (move_day.getUTCDate()+1 >= 20)
              {
                  var n=move_day.setMonth(move_day.getMonth()+1,1);
                  var dt = new Date(n);
                  var lastDay = new Date(dt.getFullYear(), dt.getMonth() + 1, 0)
                  rawInput1 = lastDay;
              }
              else
              {
                  var lastDay = new Date(move_day.getFullYear(), move_day.getMonth()+ 1, 0)
                  rawInput1 = lastDay;
              }
           $('input[name="renting_dates"]').daterangepicker({
              startDate: dob,
              endDate: rawInput1,
            });
        }

        var prd_id = document.querySelector('.product_id').value;

        rpc.query({
          route: "/bluespace/datevalidation",
          params: {
              dates: dob,
              prd_id: prd_id,
            },
          }).then(function (result) {
            $("#display").html(' ');
            if (result.msg) {
              $("#display").html(result.msg);
            }
        });
      }
    });

  //For Hour and Minute

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

  $('#MoveOutDateOfc').datepicker({
     changeMonth: true,
     changeYear: true,
     dateFormat: 'mm/dd/yy',
     minDate: 0,

    onClose: function(dateText, inst) {
        var iMonth = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
        var iYear = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
        var selDate=$(this).datepicker(new Date(iYear, iMonth, 1));
     },
     beforeShow: function() {
      var dob = $("#MoveOutDateOfc").val();
      var selDate = $(this).val().length > 0
       if (dob)
       {
          var iYear = new Date().getFullYear();
          var iMonth = new Date().getMonth();
          $(this).datepicker('option', 'defaultDate', new Date(iYear, iMonth, 1));
          //$(this).datepicker('option', 'defaultDate', new Date(iYear, iMonth, 1));
       }
    }
  });

   $("#MoveOutDateOfc").on("change.datepicker", ({date}) => {
      var dob = $("#MoveInDate").val();
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
        var start_hours=document.querySelector('#start_hours').value;
        var start_minits=document.querySelector('#start_minits').value;
        //var end_hours = document.querySelector('#end_hours').value;
        //var end_minits = document.querySelector('#end_minits').value;

        const move_day = new Date(dob);
        const newDate = addHours(move_day, parseInt(start_hours));
        var dob1=add_minutes(new Date(newDate), parseInt(start_minits));

        var move_out_date = $("#MoveOutDateOfc").val()
        $('#end_hours option:eq(18)').attr('selected', true);
        $('#end_minits option:eq(00)').attr('selected', true);
        var move_day1 = new Date(move_out_date);
        const newDate1 = addHours(move_day1, 18);
        var rawInput1=add_minutes(new Date(newDate1), 0);
        console.log(rawInput1+":::move_day>>>>>>>>>>>>>>>>>>>>"+move_day1);
        $('input[name="renting_dates"]').daterangepicker({
          startDate: dob1,
          endDate: rawInput1,
          timePicker: true,
          timePicker24Hour: true,
          locale: {
            format: 'YYYY/MM/DD HH:mm'
          },
        });
        rpc.query({
          route: "/bluespace/daysvalidation",
          params: {
              in_date: dob1,
              out_date: rawInput1
            },
          }).then(function (result) {
            $("#display").html(' ');
            if (result.msg) {
              $("#display").html(result.msg);
            }
        });
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

});



