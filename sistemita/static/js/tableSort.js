let searchParams = new URLSearchParams(window.location.search);
if(searchParams.has('order_by')){
    let param = searchParams.get('order_by');
    if(param.charAt(0) === '-'){
	param = param.substring(1);
	let column = $('thead tr').find(`[data-order='${param}']`);
	column.addClass('desc');
    } else {
	let column = $('thead tr').find(`[data-order='${param}']`);
	column.addClass('asc');
    }
}

var $sortable = $('.sortable');
$sortable.on('click', function(){
    var $this = $(this);
    var order_by = $this[0].dataset.order;
    var asc = $this.hasClass('asc');
    var desc = $this.hasClass('desc');
    const parser = new URL(window.location);

    $sortable.removeClass('asc').removeClass('desc');
    if (!asc && !desc) {
	$this.addClass('asc');
	parser.searchParams.set('order_by', order_by);
    } else {
	if(asc){
	    $this.addClass('asc');
	    order_by = `-${order_by}`;
	    parser.searchParams.set('order_by', order_by);
	} else{
	    parser.searchParams.delete('order_by')
	}

    }
    window.location = parser.href;
});
