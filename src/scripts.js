function noLinenumbers() {
	popup = window.open('', 'name', 'height=600, width=600, scrollbars=1')
	pbody = popup.document
	table = document.getElementById("source")
	pbody.write("<html><head><title>Display source file</title></head>")
	pbody.write('<body>')
	for (row in table.rows) {
		pbody.write(table.rows[row].cells[1].innerHTML + "<br/>\n")
	}
	pbody.write("</body></html>")
	pbody.close()
}

function AJAXRequest(weburl) {
	// initialize AJAX object
	if ( window.XMLHttpRequest ) {
		AJAX = new XMLHttpRequest();
	} else {
		// patch for IE >:P
		AJAX = new ActiveXObject("Microsoft.XMLHTTP");
	}

	// function to present the result
	AJAX.onreadystatechange = function() {
		if ( AJAX.readyState == 4 ) {
			document.getElementById("Sresult").innerHTML =
				AJAX.responseText;
		} else {
			document.getElementById("Sresult").innerHTML = "Searching...";
		}
	}

	// preparing search elements
	tag = document.getElementById("Stag").value;
	proj = document.getElementById("Sproj").value;

	// sending search data
	AJAX.open("POST", weburl, true);
	AJAX.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	AJAX.send("tag="+tag+"&proj="+proj);
}

function AJAXPrepare(weburl, tag) {
	document.getElementById("Stag").value = tag;
	AJAXRequest(weburl);
}