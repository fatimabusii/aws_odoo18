odoo.define('website_extra_info.date_validation', function (require) {
'use strict';
    $("#used_for_text").hide();
  $("#what_content_used").hide();
  $("#what_activity_occur").hide();
  
  const select = document.getElementById('unit_used_for');
  if (select != null)
  {
    select.addEventListener('change', function handleChange(event) {
      console.log(event.target.value);
      if (event.target.value == 'other')
        $("#used_for_text").show(300);
       else
      {
        $("#used_for_text").hide();
      }
      });
  }
  const what_content = document.getElementById('what_content');
  if (what_content !=null)
  {
    what_content.addEventListener('change', function handleChange(event) {
    console.log(event.target.value);
    if (event.target.value == 'other')
      $("#what_content_used").show(300);
     else
    {
      $("#what_content_used").hide();
    }
    });
  }
  
  const what_activity = document.getElementById('what_activity');
  if (what_activity != null)
  {
    what_activity.addEventListener('change', function handleChange(event) {
    console.log(event.target.value);
    if (event.target.value == 'other')
      $("#what_activity_occur").show(300);
     else
    {
      $("#what_activity_occur").hide();
    }
    });
  }

    //$("#required_field").text("All lease terms and conditions");
    //$("#required_field").hide();
    //$("#checkall").hide();
    //$(".s_website_form_send").prop("disabled",true);

    var is_approve = $('#is_approved').val()
    // Changed 's_website_form_send' to 'btn_erpweb'
    // if use s_website_form_send then contactus submit button not working
    if ( is_approve == 1){
       $(".btn_erpweb").prop("disabled",false);
    }
    else {
      $(".btn_erpweb").prop("disabled",true);
    }

    $('#checkall').change(function () {
      $('.cb-element').prop('checked',this.checked);
      $(".btn_erpweb").prop("disabled",false);
    });

    $('.cb-element').change(function () {
     if ($('.cb-element:checked').length == $('.cb-element').length){
      $('#checkall').prop('checked',true);
      $(".btn_erpweb").prop("disabled",false);
     }
     else {
      $('#checkall').prop('checked',false);
       $(".btn_erpweb").prop("disabled",true);
     }
    });

    var is_ofc_brd = $('#is_ofc_brd').val();

    $('.btn_erpweb').click(function (event) {
      let unit_used_for = $("#unit_used_for option:selected").val();
      let what_content = $("#what_content option:selected").val();
      let what_activity = $("#what_activity option:selected").val();

      if (!unit_used_for && is_ofc_brd == 0) {
        alert("Please select the Unit Use!!!");
        event.preventDefault();
        return false;
      } else if (!what_content && is_ofc_brd == 0) {
        alert("Please select the Contents in Unit!!!");
        event.preventDefault();
        return false;
      } else if (!what_activity && is_ofc_brd == 0) {
        alert("Please select the Activity in Unit!!!");
        event.preventDefault();
        return false;
      } else if($('.cb-element').is(':checked')) {
        var is_true = $('.cb-element').prop('checked',true);
          $("#required_field").hide();
      } else if (is_approve == 1) {
        $("#required_field").hide();
      } else {
        /*$("#required_field").text("Please all are required");*/
        alert("Please read and accept all lease terms and conditions");
        event.preventDefault();
      }

    });

    var next_count = 2
    $('#add_more').click(function() {
        console.log(next_count)
        var files = "";
        files =  '<input class="form-control" type="file" name="file_input_'+ next_count +'"/>'
        $("#file_input_list").append(files)
        next_count++;
    });

    $("#eft_display").text("Please note access to the facility will be granted once payment reflects on our account. Alternatively pay using a credit card to secure immediate access from your indicated move in date/time.");
    $("#eft_display").hide();

    $("#eft_display_ofc").text("EFT only accepted as payment method if booking is more than 1 day in advance.");
});
