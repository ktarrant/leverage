
class properties(dict):

	def __setitem__(self, key, value):
		keys = key.split(",")
		if len(keys) == 1:
			super(properties, self).__setitem__(key, value)
		else:
			if keys[0] not in self:
				self[keys[0]] = properties()
			self[keys[0]][",".join(keys[1:])] = value

	def __getitem__(self, key):
		keys = key.split(",")
		if len(keys) == 1:
			return super(properties, self).__getitem__(key)
		elif keys[0] in self:
			return self[keys[0]][",".join(keys[1:])]
		else:
			raise KeyError(keys[0])