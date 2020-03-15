$(document).ready(function(){
        $('#update-groceries').on('submit', (evt) => {
            evt.preventDefault();
            const inputs = [];
            $.each($("input[name='ids']:not(:checked)"), function(){
                inputs.push($(this).val());
            });
            const formInputs = {
                'item_ids': inputs
            }
            console.log(formInputs);
            $.post('/update-groceries', formInputs, (res) => {
                $("input[name='ids']:not(:checked)").each( function(){
                $(this).parents("tr").remove();
                });
            });
        });
    });