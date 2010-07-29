// take the entire source code and display it without annoying linenumbers
// TODO: make it using the pygments HTML formatter (AJAXify)
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

// wrapper for AJAXRequest. Use it each time you want to pop-up the
// search results without actually entering text into search textbox.
function AJAXPrepare(weburl, tag) {
	document.getElementById("Stag").value = tag;
	AJAXRequest(weburl);
}

function highlight() {
	url = window.location.href;
	splitted = url.split('#');
	if (splitted.length < 2)
		return;
	line = "l" + splitted[1];
	document.getElementById(line).style.background = '#AAEEFF';
}

function AJAXConfigStore(weburl) {
	if ( window.XMLHttpRequest ) {
		AJAX = new XMLHttpRequest();
	} else {
		AJAX = new ActiveXObject("Microsoft.XMLHTTP");
	}

	AJAX.onreadystatechange = function() {
		if ( AJAX.readyState == 4 ) {
			document.getElementById("AJAXMSG").innerHTML =
				AJAX.responseText;
		} else {
			document.getElementById("AJAXMSG").innerHTML = "Processing data...";
		}
	}

	dataArray = [];
	pattern = /\//;
	for (i in document.form1.elements) {
		if (pattern.test(document.form1.elements[i].name) ) {
			name = document.form1.elements[i].name;
			value = document.form1.elements[i].value;
			dataArray.push( '("' + name + '","' + value + '")' );
		}
	}
	data = escape('[' + dataArray.join(',') + ']');
	document.getElementById("AJAXMSG").innerHTML = "Sending configuration stream:</br>" + data;

	AJAX.open("POST", weburl, true);
	AJAX.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	AJAX.send("data=" + data);
}

function toggleCollapse(idname) {
	if ( document.getElementById(idname).style.display=='' ) {
		document.getElementById(idname).style.display = 'none';
	} else {
		document.getElementById(idname).style.display = '';
	}
}