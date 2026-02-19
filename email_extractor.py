#!/usr/bin/env python3
"""
Simple GUI Email Extractor (No extra dependencies)
"""

import re
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

class SimpleEmailExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Extractor")
        self.root.geometry("600x500")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.deduplicate = tk.BooleanVar(value=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = ttk.Label(self.root, text="Email Extractor", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Input Frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(input_frame, text="Input File:").pack(anchor=tk.W)
        
        input_subframe = ttk.Frame(input_frame)
        input_subframe.pack(fill=tk.X, pady=5)
        
        ttk.Entry(input_subframe, textvariable=self.input_file, width=40).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(input_subframe, text="Browse", command=self.browse_input).pack(side=tk.LEFT)
        
        # Output Frame
        output_frame = ttk.Frame(self.root)
        output_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(output_frame, text="Output File:").pack(anchor=tk.W)
        
        output_subframe = ttk.Frame(output_frame)
        output_subframe.pack(fill=tk.X, pady=5)
        
        ttk.Entry(output_subframe, textvariable=self.output_file, width=40).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(output_subframe, text="Browse", command=self.browse_output).pack(side=tk.LEFT)
        
        # Options
        ttk.Checkbutton(
            self.root, 
            text="Remove duplicate emails",
            variable=self.deduplicate
        ).pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Extract Emails", command=self.extract).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)
        
        # Preview
        ttk.Label(self.root, text="Extracted Emails:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        self.preview = scrolledtext.ScrolledText(self.root, height=10, width=60)
        self.preview.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Status
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_input(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file:
            self.input_file.set(file)
            if not self.output_file.get():
                base = os.path.splitext(file)[0]
                self.output_file.set(f"{base}_emails.txt")
    
    def browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file:
            self.output_file.set(file)
    
    def extract(self):
        input_path = self.input_file.get()
        output_path = self.output_file.get()
        
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid input file")
            return
        
        if not output_path:
            messagebox.showerror("Error", "Please specify output file")
            return
        
        # Run in thread
        thread = threading.Thread(target=self.do_extraction, args=(input_path, output_path), daemon=True)
        thread.start()
    
    def do_extraction(self, input_path, output_path):
        self.root.after(0, lambda: self.status.config(text="Extracting..."))
        
        try:
            with open(input_path, 'r') as f:
                text = f.read()
            
            emails = re.findall(r'\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}\b', text)
            
            if self.deduplicate.get():
                emails = list(dict.fromkeys([e.lower() for e in emails]))
                emails = [e.title() for e in emails]  # Restore capitalization
            
            with open(output_path, 'w') as f:
                for email in emails:
                    f.write(f"{email}\n")
            
            # Update UI
            self.root.after(0, self.update_preview, emails, output_path)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def update_preview(self, emails, output_path):
        self.preview.delete(1.0, tk.END)
        for email in emails[:20]:
            self.preview.insert(tk.END, f"{email}\n")
        
        if len(emails) > 20:
            self.preview.insert(tk.END, f"\n... and {len(emails) - 20} more")
        
        self.status.config(text=f"Extracted {len(emails)} emails to {os.path.basename(output_path)}")
        messagebox.showinfo("Success", f"Extracted {len(emails)} emails")
    
    def clear(self):
        self.input_file.set("")
        self.output_file.set("")
        self.preview.delete(1.0, tk.END)
        self.status.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleEmailExtractorGUI(root)
    root.mainloop()