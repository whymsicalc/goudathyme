$('#add-to-kitchen').on('submit', (evt) => {
  evt.preventDefault();

  const formInputs = $(`#to-add`).serialize();

  $.post('/add-to-kitchen', formInputs, (res) => {
    for (const item of res) {
      let expiration = "None";
      if (item.expiration_date) {
        expiration = item.expiration_date
      };
      let low = "None";
      if (item.running_low) {
        low = item.running_low
      };
      let notes = "None";
      if (item.notes) {
        const notes = item.notes
      };
      let name_td = ""
      if (item.api_id != null) {
        name_td = "<td><a class='link' href='/ingredient/" + item.api_id + "'>" + item.ingredient_name + "</a></td>"
      } else {
        name_td = "<td>" + item.ingredient_name + "</td>"
      };
      $('#current-ings').append(
          `<tr data-item_id="${item.item_id}"">
              ${name_td}
              <td>${expiration}</td>
              <td>${low}</td>
              <td>${notes}</td>
              <td class="thin">
                <a class="add" title="Update" data-toggle="tooltip" data-placement="left"><i class="material-icons">&#xE03B;</i></a>
                <a class="edit" title="Edit" data-toggle="tooltip" data-placement="left"><i class="material-icons">&#xE254;</i></a>
                <a class="delete" title="Delete" data-toggle="tooltip" data-placement="left"><i class="material-icons">&#xE872;</i></a>
              </td>
          </tr>`
          );
      $('[data-toggle="tooltip"]').tooltip({ trigger: "hover" });
  }});
  // Clear select box each time user adds ingredient
  $(".new-ingredient").val('').trigger('change');
});
// Let user add new ingredient (to their list and to ingredients table)
$(document).ready(function() {
  $('.new-ingredient').select2({
    // Allows user to create new option if it isn't in options
    tags: true,
    placeholder: "Enter an Ingredient",
    // Creates new tag when "," is entered
    tokenSeparators: [','],
    createTag: function (params) {
      const term = $.trim(params.term);

      if (term === '') {
        return null;
      }

      return {
        id: term,
        text: term,
        newTag: true // add additional parameters
      }
    }
  });
});
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip({ trigger: "hover" });
  // Edit row on edit button click
  $(document).on("click", ".edit", function(){
    const months = {
      'January' : '01',
      'February' : '02',
      'March' : '03',
      'April' : '04',
      'May' : '05',
      'June' : '06',
      'July' : '07',
      'August' : '08',
      'September' : '09',
      'October' : '10',
      'November' : '11',
      'December' : '12'
    }
      $(this).parents("tr").find("td:nth-child(2)").each(function(){
        console.log($(this).text());
        let new_date = ""
        if ($(this).text() != "None"){
            const split = $(this).text().split(" ");
            const month = months[split[1]];
            const date = split[2].slice(0,2);
            const year = split[3];
            new_date = year + "-" + month + "-" + date
          };
          $(this).html('<input type="date" id="date" class="form-control" value="' + new_date + '">');
      });
      $(this).parents("tr").find("td:nth-child(3)").each(function(){
          $(this).html('<input type="checkbox" id="low" ' + 
            (($(this).text() === "True") ? 'checked' : '') + '>');
      });
      $(this).parents("tr").find("td:nth-child(4)").each(function(){
          $(this).html('<input type="text" id="notes" class="form-control" value="' + $(this).text() + '">');
      });     
      $(this).parents("tr").find(".add, .edit").toggle();
  });
  // Delete row on delete button click
  $(document).on("click", ".delete", (evt) => {
    const row = $(evt.target).parents("tr");
    $('[data-toggle="tooltip"]').tooltip("hide");
    const formInputs = {
      'item_id': row.data('item_id')
    };
    row.remove();
    $.post('/delete-row', formInputs, (res) => {});
    })
});

$('#update-kitchen').on('click', '.add', (evt) => {
  evt.preventDefault();
  const row = $(evt.target).parents("tr");
   const formInputs = {
      'item_id': row.data('item_id'),
      'date': row.find('#date').val(),
      'low': row.find('#low').is(':checked'),
      'notes': row.find('#notes').val()
    };

  $.post('/update-kitchen', formInputs, (res) => {
    row.find("td:nth-child(2)").each(function(){
        $(this).html((res.expiration_date == null) ? 'None':res.expiration_date);
      });
    row.find("td:nth-child(3)").each(function(){
        $(this).html((res.running_low == true) ? 'True':'False');
      });
    row.find("td:nth-child(4)").each(function(){
        $(this).html(res.notes);
      });
    row.find(".add, .edit").toggle();
  });
});