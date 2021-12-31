class HtmlResult:

	blocks = []
	html = ""

	def __init__(self):
		with open("example.html",'r') as f:
			self.html = f.read()

	def make_one_block(self, fio: str, link_to: str, picture_links: list):
		photos = []

		for link in picture_links:
			photos.append(f"""
					<center>
						<img src="{link}">
					</center>
					<br>
			""")

		string = ""
		for a in photos:
			string += a

		block = f"""
				<details>
					<summary>
						<a href = "{link_to}">{fio}</a> (≈{len(picture_links)})
					</summary>
					{string}
				</details>
			"""
		self.blocks.append(block)

	def result(self):
		
		n = self.html.find("<div>") + 5
		
		new = ""
		for block in self.blocks:
			new += block
		
		self.html = self.html[:n] + new + self.html[n:]
		return self.html