import random, os.path, shutil

corruptionDebug = True

class headerlookup:
	def extension(ext: str):
		match ext.lower().removeprefix('.'):
			case 'wav': 			 return 44
			case 'mp3': 			 return 1024
			case 'ogg': 			 return 256
			case 'flac': 			 return 512
			case 'm4a'|'alac'|'aac': return 1024
			case _: 				 return 1024

class corrupt:
	def corruption_wrapper(file_path: str, type: str, options= [], folder_path = ""):
		# path handling
		if not os.path.isfile(file_path):
			raise FileNotFoundError(f"File not found: {file_path}")
		file_name = os.path.basename(file_path)

		if folder_path == "":
			temp_path = os.path.join(os.getcwd(), "temp", os.path.splitext(file_name)[0]+"_corrupted"+os.path.splitext(file_name)[1])
			os.makedirs(os.path.join(os.getcwd(), "temp"))
		else: temp_path = os.path.join(folder_path, os.path.splitext(file_name)[0]+"_corrupted"+os.path.splitext(file_name)[1])

		# apply corruption
		if not options:
			match type.lower():
				case 'simple': corrupt.file_corrupter_mask_simple(file_path, temp_path, headerlookup.extension(os.path.splitext(file_path)[1]))
				case 'random': corrupt.file_corrupter_random(file_path, temp_path, options[0], headerlookup.extension(os.path.splitext(file_path)[1]))
				case 'biased': corrupt.file_corrupter_mask_biased(file_path, temp_path, headerlookup.extension(os.path.splitext(file_path)[1]))
				case 'evil'  : corrupt.file_corrupter_evil(file_path, temp_path, headerlookup.extension(os.path.splitext(file_path)[1])) # best with .wav!
				case _:        None 
		else:
			#! I refuse to write warnings or error handling for this. if you fuck up using them that is not my problem
			if type.lower() == 'simple': 
				corrupt.file_corrupter_mask_simple(file_path, temp_path, frequency=options[0], mask=options[1], fror=options[2])
			if type.lower() == 'random':
				corrupt.file_corrupter_random(file_path, temp_path, options[0])
			if type.lower() == 'biased':
				corrupt.file_corrupter_mask_biased(file_path, temp_path, biasLow=options[3], frequency=options[0], mask=options[1], fror=options[2])

		if temp_path and not folder_path:
			shutil.rmtree(os.path.join(os.getcwd(), "temp"))

	def file_corrupter_mask_simple(file_path_in: str, file_path_out: str, start_index= None, fror=False, frequency= 10, mask= 0x3d): # 0b01101101 #? BE
		if corruptionDebug: print(file_path_in, file_path_out, start_index, frequency, mask, fror)
		with open(file_path_in, 'rb') as f:
			data = bytearray(f.read())

		startindex = headerlookup.extension(os.path.splitext(file_path_in)[1]) if start_index is None else start_index

		i=startindex
		while i < len(data)-1:
			if data[i] != 0: data[i] ^= mask
			if data[i+2] != 0: data[i+2] ^= mask
			i += frequency
			if fror: frequency = bitmanip.ror(frequency, 1, 6)

		with open(file_path_out, 'wb') as f:
			f.write(data)

	def file_corrupter_mask_biased(file_path_in: str, file_path_out: str, biasLow= True, start_index= None, fror=False, frequency= 10, mask= 0x3d): # 0b01101101 #? BE
		if corruptionDebug: print(file_path_in, file_path_out, start_index, frequency, mask, fror, biasLow)
		with open(file_path_in, 'rb') as f:
			data = bytearray(f.read())
		LE = data[0:4] == b'RIFF'

		startindex = headerlookup.extension(os.path.splitext(file_path_in)[1]) if start_index is None else start_index

		i=startindex
		while i < len(data)-1:
			if data[i] != 0: data[i] ^= mask
			if data[i+2] != 0: data[i+2] ^= mask
			i += frequency
			i += 1 if biasLow and LE and (i + frequency) % 2 == 0 else 0
			if fror: frequency = bitmanip.ror(frequency, 1, 6)

		with open(file_path_out, 'wb') as f:
			f.write(data)

	def file_corrupter_random(file_path_in: str, file_path_out: str, chance= 0.01, start_index= None):
		with open(file_path_in, 'rb') as f:
			data = bytearray(f.read())

		startindex = headerlookup.extension(os.path.splitext(file_path_in)[1]) if start_index is None else start_index

		i=startindex
		while i < len(data):
			if data[i] != 0 and random.uniform(0.0, 1.001) <= chance:
				data[i] ^= random.choice(mask.MASKS) ^ random.choice(mask.rolranmasks(random.randint(0x0, 0xff))) % 256
				if random.uniform(0.0, 1.001) > chance:
					data[i] = bitmanip.ror(data[i], random.randint(1, 8), 8) ^ (bitmanip.rol(ord(random.choice(str(chance))) ^ 0x7e, random.randbytes(1)[0], 7))

		with open(file_path_out, 'wb') as f:
			f.write(data)

	def file_corrupter_evil(file_path_in: str, file_path_out: str, start_index= None):
		import binascii, hashlib

		seed = bitmanip.ror(int.from_bytes(bytes(os.path.basename(file_path_in), 'utf-8'), 'little'), abs(int.from_bytes(b'gay cat bois >~<') & 128), abs(int.from_bytes(bytes(os.path.basename(file_path_in), 'utf-8'), 'little') % 256)) ^ random.randint(0, int.from_bytes(random.randbytes(len(os.path.basename(file_path_in)))))
		filter = (bitmanip.rol(int.from_bytes(b'thigh highs~ uwu'), 1, 16) ^ int.from_bytes(b'HI! >:3 HI! >:3 ')).to_bytes(16, 'little')

		inserts = {0: 0xfe, 1: 0x67, 2: 203, 3: 0b10111101}

		with open(file_path_in, 'rb') as f:
			data = bytearray(f.read())

		CRC1= binascii.crc32(data)
		CRC1b=CRC1.to_bytes(4, 'little')

		if data[8:12] == b'WAVE' and data[0:4] == b'RIFF':
			sample_rate = int.from_bytes(data[24:28], 'little')
			if sample_rate == 48000:
				data[24:28] = (44100).to_bytes(4, 'little')
			else:
				data[24:28] = (48000).to_bytes(4, 'little')

			# Set bits per sample (offset 34–35) to 8-bit (0x0008 little-endian)
			data[34:36] = (8).to_bytes(2, 'little')

		if corruptionDebug: print("Precalcs donesies :o")

		startindex = headerlookup.extension(os.path.splitext(file_path_in)[1]) if start_index is None else start_index

		i=startindex; steps = 0
		while i < len(data)-270:
			if random.randint(0,100)<=13:
				for x in range(random.randint(3, 270)):
					if random.choice([0,1])==0:
						data[i+x]  %= inserts[random.randint(0,3)]
					else:data[i+x] ^= inserts[random.randint(0,3)]
			if steps % random.randint(1, 70000) == 0:
				if corruptionDebug: print(f"INSERTIONS // [{steps}] i={i}, byte={data[i]} {random.choice(["Meowies", "Nyah~ uwu", "corrution in progress bleh", ">:3", "Nothing is safe from me."])}")
			steps += 1
			i += random.choice([1, -2, 3])

		for layer in range(0,2):
			if layer == 0: layer = 0x83
			else: layer = 0xf9
			i = startindex; steps = 0
			while i < len(data)-1:
				if data[i] < layer and random.randint(0,100)<=17:
					data[i] ^= random.choice([
						random.choice(mask.MASKS) ^ random.choice(mask.rolranmasks(random.randint(0, 255))),
						bitmanip.ror(data[i], random.randint(1, 8), 8) ^ (bitmanip.rol(ord(random.choice(str(seed))) ^ 0x7e, random.randbytes(1)[0] % 6, 7)),
						CRC1b[random.randint(0,3)] | i]) % 256
					data[i] = (~(data[i] | int.from_bytes(random.choice([filter[0:8], filter[8:16]])))) & 0xff
				if steps % random.randint(1, 70000) == 0:
					if corruptionDebug: print(f"MANIPULATIONS // [{steps}] i={i}, byte={data[i]}, layer={hex(layer)} {random.choice(["Meowies", "Nyah~ uwu", "corrution in progress bleh", ">:3", "Nothing is safe from me."])}")
				steps += 1
				i += random.choice([1, -2, 3])

		i=startindex; steps = 0
		while i < len(data)-1:
			if random.randint(0,97) <= 9:
				data[i:(i+16)] = hashlib.md5(data[i:(i+16)]).digest()
			if steps % random.randint(1, 70000) == 0:
				if corruptionDebug: print(f"HASHINGS // [{steps}] i={i}, byte={data[i]} {random.choice(["Meowies", "Nyah~ uwu", "corrution in progress bleh", ">:3", "Nothing is safe from me."])}")
			steps += 1
			i += random.choice([1, -2, 3])

		with open(file_path_out, 'wb') as f:
			f.write(data)

		CRC2 = binascii.crc32(data)
		if corruptionDebug: print(f"Hash comparison (CRC): before={CRC1:032b} after={CRC2:032b}")

	def bytearray_corrupter_mask_simple(data: bytearray, start_index= None, fror=False, frequency= 10, mask= 0x3d): # 0b01101101 #? BE
		if corruptionDebug: print(data, start_index, frequency, mask, fror)

		startindex = 0 if start_index is None else start_index

		i=startindex
		while i < len(data)-1:
			if data[i] != 0: data[i] ^= mask
			if data[i+2] != 0: data[i+2] ^= mask
			i += frequency
			if fror: frequency = bitmanip.ror(frequency, 1, 6)

		return data

	def bytearray_corrupter_mask_biased(data: bytearray, biasLow= True, start_index= None, fror=False, frequency= 10, mask= 0x3d): # 0b01101101 #? BE
		if corruptionDebug: print(data, '\n', start_index, frequency, mask, fror, biasLow)

		startindex = 0 if start_index is None else start_index

		i=startindex
		while i < len(data)-1:
			if data[i] != 0: data[i] ^= mask
			if data[i+2] != 0: data[i+2] ^= mask
			i += frequency
			i += 1 if biasLow and (i + frequency) % 2 == 0 else 0
			if fror: frequency = bitmanip.ror(frequency, 1, 6)

		return data

	def bytearray_corrupter_random(data: bytearray, chance= 0.01, start_index= None):

		startindex = 0 if start_index is None else start_index

		i=startindex
		while i < len(data):
			if data[i] != 0 and random.uniform(0.0, 1.001) <= chance:
				data[i] ^= random.choice(mask.MASKS) ^ random.choice(mask.rolranmasks(random.randint(0x0, 0xff))) % 256
				if random.uniform(0.0, 1.001) > chance:
					data[i] = bitmanip.ror(data[i], random.randint(1, 8), 8) ^ (bitmanip.rol(ord(random.choice(str(chance))) ^ 0x7e, random.randbytes(1)[0], 7))

		return data

	def bytearray_corrupter_evil(data: bytearray, start_index= None):
		import binascii, hashlib

		seed = bitmanip.ror(int.from_bytes(data[3:5], 'little'), abs(int.from_bytes(b'gay cat bois >~<') & 128), abs(int.from_bytes(data[0:2], 'little') % 256)) ^ random.randint(0, int.from_bytes(random.randbytes(data[2].bit_count())))
		filter = (bitmanip.rol(int.from_bytes(b'thigh highs~ uwu'), 1, 16) ^ int.from_bytes(b'HI! >:3 HI! >:3 ')).to_bytes(16, 'little')

		inserts = {0: 0xfe, 1: 0x67, 2: 203, 3: 0b10111101}

		CRC1= binascii.crc32(data)
		CRC1b=CRC1.to_bytes(4, 'little')

		if data[8:12] == b'WAVE' and data[0:4] == b'RIFF':
			sample_rate = int.from_bytes(data[24:28], 'little')
			if sample_rate == 48000:
				data[24:28] = (44100).to_bytes(4, 'little')
			else:
				data[24:28] = (48000).to_bytes(4, 'little')

			# Set bits per sample (offset 34–35) to 8-bit (0x0008 little-endian)
			data[34:36] = (8).to_bytes(2, 'little')

		if corruptionDebug: print("Precalcs donesies :o")

		startindex = 0 if start_index is None else start_index

		i=startindex; steps = 0
		while i < len(data)-270:
			if random.randint(0,100)<=13:
				for x in range(random.randint(3, 270)):
					if random.choice([0,1])==0:
						data[i+x]  %= inserts[random.randint(0,3)]
					else:data[i+x] ^= inserts[random.randint(0,3)]
			if steps % random.randint(1, 70000) == 0:
				if corruptionDebug: print(f"INSERTIONS // [{steps}] i={i}, byte={data[i]} {random.choice(["Meowies", "Nyah~ uwu", "corrution in progress bleh", ">:3", "Nothing is safe from me."])}")
			steps += 1
			i += random.choice([1, -2, 3])

		for layer in range(0,2):
			if layer == 0: layer = 0x83
			else: layer = 0xf9
			i = startindex; steps = 0
			while i < len(data)-1:
				if data[i] < layer and random.randint(0,100)<=17:
					data[i] ^= random.choice([
						random.choice(mask.MASKS) ^ random.choice(mask.rolranmasks(random.randint(0, 255))),
						bitmanip.ror(data[i], random.randint(1, 8), 8) ^ (bitmanip.rol(ord(random.choice(str(seed))) ^ 0x7e, random.randbytes(1)[0] % 6, 7)),
						CRC1b[random.randint(0,3)] | i]) % 256
					data[i] = (~(data[i] | int.from_bytes(random.choice([filter[0:8], filter[8:16]])))) & 0xff
				if steps % random.randint(1, 70000) == 0:
					if corruptionDebug: print(f"MANIPULATIONS // [{steps}] i={i}, byte={data[i]}, layer={hex(layer)} {random.choice(["Meowies", "Nyah~ uwu", "corrution in progress bleh", ">:3", "Nothing is safe from me."])}")
				steps += 1
				i += random.choice([1, -2, 3])

		i=startindex; steps = 0
		while i < len(data)-1:
			if random.randint(0,97) <= 9:
				data[i:(i+16)] = hashlib.md5(data[i:(i+16)]).digest()
			if steps % random.randint(1, 70000) == 0:
				if corruptionDebug: print(f"HASHINGS // [{steps}] i={i}, byte={data[i]} {random.choice(["Meowies", "Nyah~ uwu", "corrution in progress bleh", ">:3", "Nothing is safe from me."])}")
			steps += 1
			i += random.choice([1, -2, 3])

		CRC2 = binascii.crc32(data)
		if corruptionDebug: print(f"Hash comparison (CRC): before={CRC1:032b} after={CRC2:032b}")

		return data

class level:
	high = "high"
	low = "low"

class bitmanip:
	def rol(val, r_bits, width=8):
		return ((val << r_bits) & (2**width - 1)) | (val >> (width - r_bits))

	def ror(val, r_bits, width=8):
		return ((val >> r_bits) | (val << (width - r_bits))) & (2**width - 1)

class mask:
	MASKS = [0x07, 0x16, 0x2b, 0x3d, 0x5c, 0x7e, 0x91, 0xaa, 0xf1, 0xff]

	@staticmethod
	def rolranmasks(maskval=MASKS[5]):
		mlist = [maskval]; bits=max(8, maskval.bit_length())
		for _ in range(bits):
			maskval = bitmanip.rol(maskval, 1, bits) ^ (maskval ^ 0x0c)
			mlist.append(maskval)
		return mlist

	arraylevel = {
		level.high : rolranmasks(MASKS[6]),
		level.low : MASKS[0:4]
	}

