# Tektrove

Welcome to **Tektrove**!  
This project enables users to upload and query valid documents, such as videos, text files, or PDFs.

## Overview
Tektrove allows you to upload documents and query them through a web interface. Supported document types are validated upon upload, and relevant information can be extracted from them for easy querying.  

**Technologies Used**: Python, RAG (Retrieval-Augmented Generation)

## Features
- Upload and manage video, text, and PDF files
- Query documents to retrieve relevant information
- Automated folder management for uploaded documents

## Installation Guide

### Step 1: Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/RaviTejaJGit/Tektrove
```

### Step 2: Run Installation Script
Double-click on installation.bat to install all necessary packages and dependencies.

### Step 3: Configure Environment Variables
Update your API keys and other environment variables in the .env file as needed.

### Step 4: Run the Application
Run the application by executing:
```bash
python app.py
```

### Step 5: Upload Your Documents
Place the documents (e.g., videos, .txt files, .pdf files) into the Upload_here folder.
Documents will automatically move to the videos folder once the database updates.

### Step 6 : Step 6: Open the Application in a Browser
Open the URL provided in your terminal after running app.py.
Page 1 will appear. Enter your query in the search bar to retrieve relevant information.

## Interface Screenshots
Here’s a preview of the interface pages:

### Page 1: Query Interface

![page1](https://github.com/user-attachments/assets/8e40706d-04d3-4521-b662-c2fde2922b61)

### Page 2 : Results with video Reference(s)
![page2](https://github.com/user-attachments/assets/2a8945ff-b553-4624-8e55-5573f2f63fee)

### Page 3 : Summary of the Document 
![page3](https://github.com/user-attachments/assets/4a068787-7cef-423f-9d2d-0eeb1f21334c)
