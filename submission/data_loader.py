from tqdm import tqdm
import pandas as pd
import json
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class MaritimeDataLoader:
    def __init__(self, persist_dir="./maritime_db", model_name="all-MiniLM-L6-v2"):
        self.persist_dir = persist_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def process_csv(self, csv_path, batch_size=5000):
        """Process CSV and create vector store with progress bars"""
        print(f"Loading CSV from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        print("Processing documents...")
        documents = []
        # Progress bar for document processing
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing articles"):
            try:
                content_dict = json.loads(row['content'].strip().replace('event: data\ndata: ', ''))
                actual_content = content_dict.get('content', '')
                title = content_dict.get('title', '')
                url = content_dict.get('url', row.get('link', ''))
                combined_text = f"Title: {title}\nURL: {url}\n\nContent: {actual_content}"
                chunks = self.text_splitter.split_text(combined_text)
                documents.extend(chunks)
            except json.JSONDecodeError as e:
                print(f"Error processing row: {e}")
                combined_text = f"Search Query: {row['search_query']}\nURL: {row['link']}\n\nContent: {row['content']}"
                chunks = self.text_splitter.split_text(combined_text)
                documents.extend(chunks)
        
        total_chunks = len(documents)
        print(f"\nTotal chunks to process: {total_chunks}")
        
        # Calculate total batches for progress bar
        total_batches = (total_chunks + batch_size - 1) // batch_size
        
        # Process in batches with progress bar
        with tqdm(total=total_batches, desc="Processing batches") as pbar:
            for i in range(0, total_chunks, batch_size):
                batch = documents[i:i + batch_size]
                
                if i == 0:
                    # Create new vector store for first batch
                    vector_store = Chroma.from_texts(
                        texts=batch,
                        embedding=self.embeddings,
                        persist_directory=self.persist_dir
                    )
                else:
                    # Add subsequent batches to existing store
                    vector_store.add_texts(texts=batch)
                
                # Persist after each batch
                vector_store.persist()
                
                # Update progress bar
                pbar.update(1)
                # Add batch statistics
                pbar.set_postfix({
                    'Chunks': f"{min(i + batch_size, total_chunks)}/{total_chunks}",
                    'Batch': f"{i//batch_size + 1}/{total_batches}"
                })
        
        print(f"\nVector store created and persisted at {self.persist_dir}")
        return vector_store

def main():
    # Create data loader
    loader = MaritimeDataLoader()
    
    # Process CSV files
    csv_files = [
        "maritime_data.csv",  # Update with your actual CSV file path
    ]
    
    for csv_file in csv_files:
        loader.process_csv(csv_file)
        print(f"Finished processing {csv_file}")

if __name__ == "__main__":
    main()