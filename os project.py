import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import time

# Simulated Disk with blocks (each block can hold data or be free)
class Disk:
    def __init__(self, size=100):
        self.size = size
        self.blocks = ["FREE"] * size  # Initialize all blocks as free
        self.directory = {}  # File name -> list of block indices

    def allocate_space(self, file_name, file_size):
        free_blocks = [i for i, block in enumerate(self.blocks) if block == "FREE"]
        if len(free_blocks) < file_size:
            return False  # Not enough space
        allocated_blocks = random.sample(free_blocks, file_size)
        for block in allocated_blocks:
            self.blocks[block] = file_name
        self.directory[file_name] = allocated_blocks
        return True

    def delete_file(self, file_name):
        if file_name not in self.directory:
            return False
        for block in self.directory[file_name]:
            self.blocks[block] = "FREE"
        del self.directory[file_name]
        return True

    def optimize(self):
        # Move files to contiguous blocks for faster access
        new_blocks = ["FREE"] * self.size
        current_index = 0
        for file_name, blocks in self.directory.items():
            for _ in range(len(blocks)):
                new_blocks[current_index] = file_name
                current_index += 1
        self.blocks = new_blocks
        # Update directory with new contiguous block indices
        current_index = 0
        for file_name in self.directory.keys():
            file_size = len(self.directory[file_name])
            self.directory[file_name] = list(range(current_index, current_index + file_size))
            current_index += file_size

    def simulate_crash(self):
        # Simulate a disk crash by corrupting some blocks
        corrupted_blocks = random.sample(range(self.size), int(self.size * 0.1))  # 10% corruption
        for block in corrupted_blocks:
            if self.blocks[block] != "FREE":
                self.blocks[block] = "CORRUPTED"
        # Update directory to reflect corruption
        for file_name in list(self.directory.keys()):
            blocks = self.directory[file_name]
            if any(self.blocks[block] == "CORRUPTED" for block in blocks):
                del self.directory[file_name]

    def recover(self):
        # Recover by marking corrupted blocks as free and rebuilding directory
        for i in range(self.size):
            if self.blocks[i] == "CORRUPTED":
                self.blocks[i] = "FREE"

    def get_status(self):
        free_space = self.blocks.count("FREE")
        used_space = self.size - free_space
        return f"Free Space: {free_space} blocks\nUsed Space: {used_space} blocks\nFiles: {len(self.directory)}"

    def get_directory(self):
        return "\n".join([f"{file}: {blocks}" for file, blocks in self.directory.items()])

# GUI Application
class FileSystemTool:
    def __init__(self, root):
        self.disk = Disk(size=100)
        self.root = root
        self.root.title("File System Recovery and Optimization Tool")
        self.root.geometry("600x500")

        # Labels and Inputs
        tk.Label(root, text="File Name:").grid(row=0, column=0, padx=5, pady=5)
        self.file_name_entry = tk.Entry(root)
        self.file_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="File Size (blocks):").grid(row=1, column=0, padx=5, pady=5)
        self.file_size_entry = tk.Entry(root)
        self.file_size_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(root, text="Create File", command=self.create_file).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(root, text="Delete File", command=self.delete_file).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(root, text="Optimize Disk", command=self.optimize_disk).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(root, text="Simulate Crash", command=self.simulate_crash).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(root, text="Recover Disk", command=self.recover_disk).grid(row=4, column=0, padx=5, pady=5)
        tk.Button(root, text="Show Status", command=self.show_status).grid(row=4, column=1, padx=5, pady=5)

        # Output Area
        self.output = scrolledtext.ScrolledText(root, width=60, height=20)
        self.output.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def create_file(self):
        file_name = self.file_name_entry.get()
        try:
            file_size = int(self.file_size_entry.get())
            if file_size <= 0 or file_size > self.disk.size:
                messagebox.showerror("Error", "Invalid file size!")
                return
            if self.disk.allocate_space(file_name, file_size):
                self.update_output(f"File '{file_name}' created with size {file_size} blocks.")
            else:
                messagebox.showerror("Error", "Not enough free space!")
        except ValueError:
            messagebox.showerror("Error", "File size must be a number!")

    def delete_file(self):
        file_name = self.file_name_entry.get()
        if self.disk.delete_file(file_name):
            self.update_output(f"File '{file_name}' deleted.")
        else:
            messagebox.showerror("Error", "File not found!")

    def optimize_disk(self):
        start_time = time.time()
        self.disk.optimize()
        end_time = time.time()
        self.update_output(f"Disk optimized in {end_time - start_time:.4f} seconds.")

    def simulate_crash(self):
        self.disk.simulate_crash()
        self.update_output("Disk crash simulated. Some files may be corrupted.")

    def recover_disk(self):
        self.disk.recover()
        self.update_output("Disk recovery completed. Corrupted blocks marked as free.")

    def show_status(self):
        status = self.disk.get_status()
        directory = self.disk.get_directory()
        self.update_output(f"Disk Status:\n{status}\n\nDirectory:\n{directory}")

    def update_output(self, message):
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, message)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemTool(root)
    root.mainloop()
