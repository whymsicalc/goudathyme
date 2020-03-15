$(document).ready(function() {
    // Create Select2 select box
    $('.select').select2();
    });
    $('.allergies').select2({
        placeholder: "Select your option(s)",
        tokenSeparators: [','],
    });
$(document).ready(function() {
    $('#find-recipes').on('submit', (evt) => {
        evt.preventDefault();
        const formInputs = {
            'user_id': $('#type').data('id'),
            'type': $('#type').val(),
            'diet': $('#diet').val(),
            'cuisine': $('#cuisine').val(),
            'intolerances': $('#intolerances').val(),
            'maxReadyTime': $('#maxReadyTime').val(),
            'sort': $('#sort').val()
            };
        $.post('/recipe-search', formInputs, (res) => {
            console.log(res);
            $('div.content').html('');
            let index = 0
            for (idx in res.results) {
                console.log(res.results[idx]);
                const result = res.results[idx];
                let col = '';
                if ([0, 3, 6].includes(index)){
                    col = `<div class="col-3 offset-1" style="overflow-x:auto;">`;
                } else {
                    col = `<div class="col-3" style="overflow-x:auto;">`;
                };
                index += 1;
                let diets = '';
                if (result['diets'].length != 0){
                    diets = `<div><b>Diet Matches:</b></div><ul>`
                    for (const idx in result['diets']){
                        diets += `<li>${result['diets'][idx]}</li>`
                        };
                    diets += '</ul>';
                    };
                let mins = '';
                if (result['readyInMinutes'] != 0 || result['readyInMinutes'] != null){
                    mins = `<div><b>Minutes to Prepare: </b>${result['readyInMinutes']}</div>`
                };
                let servings = '';
                if (result['servings'] != 0 || result['servings'] != null){
                    servings = `<div><b>Servings: </b>${result['servings']}</div><br>`
                };
                $('div.content').append(col + `<div class="card border-secondary mb-3"><img src="${result['image']}" alt="${result['title']}" style="width:100%"><div class="container"><h4 class="recipe"><b><a href="${result['sourceUrl']}">${result['title']}</a></b></h4><p class="descriptor></p>` + diets + mins + servings + `</div></div></div>`);
            };
            $('#leftHalf').hide();
            $('#rightHalf').hide();
            $(`div.form`).hide();
            $('div.darken').show();
            $(`div.results`).show();
            // $('div.body').append(`<span>More Recipes <button id="more" type="submit">>></button></span>`)
        });
    });
  });
$(document).ready(function(){
    $('[data-toggle="popover"]').popover({ trigger: "click" });
});