import webbrowser

urls = []
urls.append(("Weblinks/AW Wiki", "http://wiki.armstrong-white.com/mediawiki/index.php/Main_Page"))
urls.append(("Weblinks/Nukepedia", "http://nukepedia.com/"))

for title, url in urls:
	nuke.menu('Nuke').addCommand(title, "webbrowser.open('{url}')".format(url=url))