    function del_limit_bmp(index,del_limit_bmp_url){
        console.log(del_limit_bmp_url);
        $.ajax({
			url: "{{=URL('user','del_limit_bmp', args=[request.args(0)])}}/"+index,
			method: "POST",
			data:{
			},
            async: true,
			success: function(resp){
                console.log(resp);

                if(resp.status == 'OK'){
                    
                    $('#limit_bmp_tbody').empty();
                    for(var i=0; i<resp.limit_bmps.length;i++){
                        const row = resp.limit_bmps[i];

                        $('#limit_bmp_tbody').append(`<tr>
                        <td>`+(i+1)+`</td>
                        <td>`+row[1]+`</td>
                        <td>`+row[4]+`</td>
                        <td>`+row[5]+`</td>
                        <td align='right'><a href="#" class="btn btn-danger btn-sm" onclick="del_limit_bmp(`+i+`);"><i class="fas fa-trash"></i></a></td>
                    </tr>`)
                        
                    }
                }
			},
			error: function() {
				console.log("Error deleting fixed bmp.");
				
			}
		});
    }

    function update_cost(){
        var bmp_id = $("#bmp_id").val();
        var bmp_list = JSON.parse(bmp_id)
        $("#cost").val(bmp_list[1]);
    }

    function add_limit_bmp(){
		var ss_id = "{{=ss_id}}";
        var bmp_id = $("#bmp_id").val();
        var bmp_list = JSON.parse(bmp_id)
        var bmp_text = $("#bmp_id option:selected").html();

        var limit_unit = $("#limit_unit").val();
        //$('#limit_unit').val((limit_unit).toFixed(2));
        //var limit_unit = $("#limit_unit").val();

        var limit_cost = $("#limit_cost").val();
        //$('#limit_cost').val((limit_cost).toFixed(2));
        //var limit_cost = $("#limit_cost").val();
        $.ajax({
			url: "{{=URL('user','add_limit_bmp')}}",
			method: "POST",
			data:{
                ss_id:ss_id,
                bmp_id:bmp_list[0],
                bmp_text:bmp_text,
                limit_unit:limit_unit,
                limit_cost:limit_cost
			},
            async: true,
			success: function(resp){
                console.log(resp);

                if(resp.status == 'OK'){
                    
                    $('#limit_bmp_tbody').empty();
                    for(var i=0; i<resp.limit_bmps.length;i++){
                        const row = resp.limit_bmps[i];

                        $('#limit_bmp_tbody').append(`<tr>
                        <td>`+(i+1)+`</td>
                        <td>`+row[1]+`</td>
                        <td>`+row[4]+`</td>
                        <td>`+row[5]+`</td>
                        <td align='right'><a href="#" class="btn btn-danger btn-sm" onclick="del_limit_bmp(`+i+`);"><i class="fas fa-trash"></i></a></td>
                    </tr>`)
                        
                    }
                }
			},
			error: function() {
				console.log("Error adding limit of bmp.");
				
			}
		});
    }
    /*******************************************
	 * AMOUNT TO PERCENTAGE AND VICEVERSA
	*/

	$('.amount_unit_cost').change(function(){
		amount_unit_cost($(this));
	});

	$('.amount_unit_cost').keyup(function(){
		amount_unit_cost($(this));
	});

	function amount_unit_cost(input){
		const _class = input.data('class');
		const _type = input.data('type');
		const x = parseFloat(input.val());

		var ss_id = "{{=ss_id}}";
        var bmp_id = $("#bmp_id").val();
        var bmp_list = JSON.parse(bmp_id);
        
		if(_type == 'unit'){ //acres
			//const max_amount = parseFloat($('#'+_class+'_cost').data('max-amount'));

			$('#'+_class+'_cost').val((x*bmp_list[1]).toFixed(2));

		}else if(_type == 'amount'){//cost
			const max_amount = parseFloat(input.data('max-amount'));

			$('#'+_class+'_unit').val((x/bmp_list[1]).toFixed(2));

		}
	}


    function del_cost_bmp(index){
        $.ajax({
			url: "{{=URL('user','del_cost_bmp', args=[request.args(0)])}}/"+index,
			method: "POST",
			data:{
			},
            async: true,
			success: function(resp){
                console.log(resp);

                if(resp.status == 'OK'){
                    
                    $('#cost_bmp_tbody').empty();
                    for(var i=0; i<resp.price_bmps.length;i++){
                        const row = resp.price_bmps[i];

                        $('#cost_bmp_tbody').append(`<tr>
                        <td>`+(i+1)+`</td>
                        <td>`+row[1]+`</td>
                        <td>`+row[2]+`</td>
                        <td>`+row[3]+`</td>
                        <td align='right'><a href="#" class="btn btn-danger btn-sm" onclick="del_cost_bmp(`+i+`);"><i class="fas fa-trash"></i></a></td>
                    </tr>`)
                        
                    }
                }
			},
			error: function() {
				console.log("Error deleting fixed bmp.");
				
			}
		});
    }
    
    function add_cost_bmp(){
		var ss_id = "{{=ss_id}}";
        var bmp_id = $("#bmp_id").val();
        var bmp_list = JSON.parse(bmp_id)
        var bmp_text = $("#bmp_id option:selected").html();
        var new_cost= $("#new_cost").val();
        var former_cost= $("#cost").val();
        $("#new_cost").val("");

        $.ajax({
			url: "{{=URL('user','add_cost_bmp2')}}",
			method: "POST",
			data:{
                ss_id:ss_id,
                bmp_id:bmp_list[0],
                bmp_text:bmp_text,
                former_cost:former_cost,
                new_cost:new_cost
			},
            async: true,
			success: function(resp){
                console.log(resp);

                if(resp.status == 'OK'){
                    
                    $('#cost_bmp_tbody').empty();
                    for(var i=0; i<resp.price_bmps.length;i++){
                        const row = resp.price_bmps[i];

                        $('#cost_bmp_tbody').append(`<tr>
                        <td>`+(i+1)+`</td>
                        <td>`+row[1]+`</td>
                        <td>`+row[2]+`</td>
                        <td>`+row[3]+`</td>
                        <td align='right'><a href="#" class="btn btn-danger btn-sm" onclick="del_cost_bmp(`+i+`);"><i class="fas fa-trash"></i></a></td>
                    </tr>`)
                        
                    }
                }
			},
			error: function() {
				console.log("Error adding cost of bmp.");
				
			}
		});
    }