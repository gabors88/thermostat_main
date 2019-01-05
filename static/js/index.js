function turnHeating(status) {
	console.log("Executing callApi");
	$.get('relay/' + status, function () {
		console.log("Sent request to server");
	}).done(function () {
	        console.log("Completed request");
	}).fail(function () {
	        console.error("Relay status failure");
	});
}

function relayStatus() {
	$.get('status/relay', function () {
		console.log("sent rqst");
	}).done(function (res) {
		console.log("done");
		var msg = res
		msg = "Heating is " + msg;
		return (msg);
	}).fail(function () {
		console.log("fail")
	});
}
