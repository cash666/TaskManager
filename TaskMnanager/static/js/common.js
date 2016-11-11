$('#menu').find('li').each(function(){
	$(this).click(function(){
		$(this).siblings().removeClass('active');	
		$(this).addClass('active');
	})
})

function task_switch(obj){
	if($(obj).find(':selected').val() == '0'){
		$('#task_accept').css('display','block');
		$('#task_transfer').css('display','none');	
	} else if($(obj).find(':selected').val() == '1'){
		$('#task_accept').css('display','none');
                $('#task_transfer').css('display','none');
	} else {
		$('#task_accept').css('display','none');
                $('#task_transfer').css('display','block');
	}
}

function task2_switch(obj){
        if($(obj).find(':selected').val() == '0'){
                $('#modify_time').css('display','none');
                $('#task_transfer').css('display','none');
        } else if($(obj).find(':selected').val() == '1'){
                $('#modify_time').css('display','block');
                $('#task_transfer').css('display','none');
        } else if($(obj).find(':selected').val() == '2') {
                $('#modify_time').css('display','none');
                $('#task_transfer').css('display','none');
	} else {
		$('#modify_time').css('display','none');
                $('#task_transfer').css('display','block');
	}
}

function is_confirm(obj){
	var ret=true;
	var handle_id=$(obj).parents('table').find('td').eq(1).find(':selected').val();
	var start_time=$(obj).parents('table').find('td').eq(2).find('input').eq(0).val();
	var end_time=$(obj).parents('table').find('td').eq(2).find('input').eq(1).val();
	if (handle_id == '1'){
		if($.trim(start_time).length == 0 || $.trim(end_time).length == 0 ) {
			alert('工期不能为空');
			ret=false;
		} else {
			ret=confirm('亲,你确定已经与发起人确认好了延迟的工期时间吗?');
		}
	return ret
	}
}
