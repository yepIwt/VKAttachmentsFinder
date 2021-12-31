import asyncio
VK_API_TOKEN = ""
from vkwave.api import API
from vkwave.client import AIOHTTPClient
import html

class Core:

	__dialogs = []
	my_id = 153798115
	__api = None

	def __init__(self, token):
		api_session = API(tokens = token, clients = AIOHTTPClient())
		self.__api = api_session.get_context()

	async def get_all_dialogs(self):
		result = await self.__api.messages.get_conversations(count = 200, extended = 1, fields = "name")
		offset = 0
		while len(result.response.items) != 0:
			offset += len(result.response.items)
			for a in result.response.items:
				if a.conversation.peer.type.value == "user":
					self.__dialogs.append([0, a.conversation.peer.id])
				elif a.conversation.peer.type.value == "chat":
					self.__dialogs.append([1, a.conversation.peer.id])

			# Группы отдельно: ебанутый api vk
			for group in result.response.groups:
				self.__dialogs.append([group.name,-1 * group.id])
			result = await self.__api.messages.get_conversations(count = 200, offset = offset, extended = 1, fields = "name")
		print(f"Количество полученных диалогов: {len(self.__dialogs)}")

	async def get_all_my_attachments_from_dialog(self, dialog_id: int):
		answer = []
		offset = 0
		result = await self.__api.messages.get_history_attachments(
			peer_id = dialog_id, 
			media_type = "photo", 
			photo_sizes = 0,
			count = 200
		)
		attachs = []
		while len(result.response.items) != 0:
			offset += len(result.response.items)
			for a in result.response.items:
				if a.attachment.photo:
					if a.from_id == self.my_id:
						# find size
						for s in a.attachment.photo.sizes:
							if s.type.value == "z":
								attachs.append(s.url)
			result = await self.__api.messages.get_history_attachments(
				peer_id = dialog_id, 
				media_type = "photo", 
				photo_sizes = 0,
				count = 200,
				start_from = result.response.next_from
			)
		attachments = [dialog_id, attachs]
		return attachments

	async def get_all_my_old_attachments(self):
		await self.get_all_dialogs()
		k = []
		for n,d in self.__dialogs:
			result = await self.get_all_my_attachments_from_dialog(d)
			print("Получаем вложения из", d)
			k.append(result)
		return k

	async def get_info_about_dialog(self, dialog_id: int):
		if dialog_id < 0:
			for a,d in self.__dialogs:
				if d == dialog_id:
					fio = a
					break
			link_to = "https://vk.com/im?sel=" + str(dialog_id)
			return link_to, fio

		if dialog_id > 2000000000:
			try:
				result = await self.__api.messages.get_chat_preview(peer_id = dialog_id)
			except:
				fio = "Вы были удалены из этой беседы"
				link_to = "https://vk.com/im?sel=c" + str(2000000000 - dialog_id)
			else:
				link_to = "https://vk.com/im?sel=c" + str(result.response.preview.local_id)
				fio = result.response.preview.title
		else:
			result = await self.__api.users.get(user_ids = dialog_id)
			link_to = "https://vk.com/im?sel=" + str(result.response[0].id)
			fio = result.response[0].first_name + " " + result.response[0].last_name

		return link_to, fio


async def main():
	c = Core(VK_API_TOKEN)
	h = html.HtmlResult()

	all_my_attachs = await c.get_all_my_old_attachments()
	all_attachs_len = len(all_my_attachs)
	for a,result in enumerate(all_my_attachs):
		link_to, fio = await c.get_info_about_dialog(result[0])
		h.make_one_block(fio, link_to, result[1])
		print(f"{a+1}/{all_attachs_len}: {fio}")

	a = h.result()
	f = open("result.html",'w')
	f.write(a)
	f.close()

if __name__ == "__main__":
	asyncio.run(main())