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