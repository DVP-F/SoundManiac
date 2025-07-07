import yaml, sys, os.path
import corrupter

class ui:
	def gui():
		import tkinter as tk
		from tkinter import filedialog, messagebox

		def select_file():
			file_path = filedialog.askopenfilename()
			if file_path:
				label.config(text=f"Selected: {file_path}")

		def show_message():
			messagebox.showinfo("Hey!", "You clicked the button!")

		# Main window
		root = tk.Tk()
		root.title("SoundManiac GUI")
		root.geometry("400x200")

		# Widgets
		label = tk.Label(root, text="No file selected.")
		label.pack(pady=10)

		btn_select = tk.Button(root, text="Select File", command=select_file)
		btn_select.pack(pady=5)

		btn_run = tk.Button(root, text="Run", command=show_message)
		btn_run.pack(pady=5)

		# Run the UI loop
		root.mainloop()


class modes:
	dry = 0
	bias_low = 1
	bias_high = 2
	uwu = 4
	random = 5
	evil = 6
	ui = 7

def main():
	mask = corrupter.mask()
	launchargs = sys.argv
	match launchargs:
		case _ if 'dry' in launchargs:
			match launchargs[launchargs.index('dry')+1]:
				case 'high': masks=mask.arraylevel[corrupter.level.high]
				case 'low':  masks=mask.arraylevel[corrupter.level.low]
		# case _ if ''
		case _: masks = mask.arraylevel[corrupter.level.high]
	match launchargs:
		case _ if 'bias' in launchargs: 
			match launchargs[launchargs.index('bias')+1]:
				case 'low': mode = modes.bias_low
				case 'high': mode = modes.bias_high
		case _: mode = modes.dry

	file_path = './sounds/quack_sfx.wav'

	match launchargs:
		case _ if 'file' in launchargs:
			file_path = launchargs[launchargs.index('file')+1]
	match launchargs:
		case _ if 'suite' in launchargs:
			mode = modes.uwu
		case _ if 'evil' in launchargs:
			mode = modes.evil
		case _ if 'ui' in launchargs:
			mode = modes.ui

	file_path_out = os.path.join(file_path.removesuffix(os.path.basename(file_path)), 'tmp' if file_path.startswith(f'./tmp') else '', os.path.basename(file_path))

	print(masks, len(masks))
	match mode:
		case modes.dry:
			corrupter.corrupt.corruption_wrapper(file_path, 'simple', options=[5, masks[0], False], folder_path='./tmp')
			for i in range(1,len(masks),1):
				corrupter.corrupt.corruption_wrapper(file_path_out, 'simple', options=[12, masks[i], True], folder_path='./tmp')
		case modes.bias_low | modes.bias_high:
			corrupter.corrupt.corruption_wrapper(file_path, 'biased', options=[5, masks[0], False, True if mode==modes.bias_low else False], folder_path='./tmp')
			for i in range(1,len(masks),1):
				corrupter.corrupt.corruption_wrapper(file_path_out, 'biased', options=[12, masks[i], True, True if mode==modes.bias_low else False], folder_path='./tmp')
		case modes.uwu:
			0
		case modes.evil:
			corrupter.corrupt.corruption_wrapper(file_path, 'evil', folder_path='./tmp')
		case modes.ui:
			ui.gui()

if __name__ == "__main__":
	main()

