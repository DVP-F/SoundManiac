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
			temp_path = os.path.join(os.getcwd(), "temp", file_name)
			os.makedirs(os.path.join(os.getcwd(), "temp"))
		else: temp_path = os.path.join(folder_path, file_name)

		# apply corruption
		if not options:
			match type.lower():
				case 'simple': corrupt.file_corrupter_mask_simple(file_path, temp_path, headerlookup.extension(os.path.splitext(file_path)[1]))
				case 'random': corrupt.file_corrupter_random()
				case 'biased': corrupt.file_corrupter_mask_biased(file_path, temp_path, headerlookup.extension(os.path.splitext(file_path)[1]))
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

	def file_corrupter_random(file_path_in: str, file_path_out: str, chance= 0.01):
		""

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
		mlist = [maskval]; bits=maskval.bit_length()
		for _ in range(bits):
			maskval = bitmanip.rol(maskval, 1, bits) ^ (maskval ^ 0x0c)
			mlist.append(maskval)
		return mlist

	arraylevel = {
		level.high : rolranmasks(MASKS[6]),
		level.low : MASKS[0:4]
	}

