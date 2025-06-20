# Pre-requisites #
Consider setting up a venv or a conda env with Python version 3.10.5 for dependencies.
Do setup an .env for your API keys, for this project we used anthropic models. 

# Data Collection #
/data is the data that we collected from online existing sources and A*STAR. We mainly used the AStar_test_data and AStar_training_data.
articles_data.csv and maritime_data.csv are repositories of articles that were scraped using jina.ai. The relevant code can be found in webscrape.py

//webscrape.py
Scrapes google new, gcaptain and maritime executive on keywords (using their search engines). It accounts for repeat links should a different search query return a repeated link.

# Data Processing and Loading #
//data_loader.py
Script to load the relevant files into a vector database to be used. ChromaDb was used here. The embedding model used is all-MiniLM-L6-v2. The file embedds maritime_data.csv.Run this after scraping with webscrape.py

# Classification #
// Classification.ipynb
The notebook contains the code for our risk categorization. The data used for this is articles_data.csv which was scraped. The search queries of the articles scraped were used as the categories for classification.

# Severity Classification #
//SeverityDetection.ipynb
This notebook contains our workings for the severity classification task. Data used for this is the AStar data in /data.

# RAG Pipeline #
//maritime-chain.ipynb
Loads in the models pickled from Classification.ipynb in /models for the risk categorisation in the MaritimeClassifier class. The severity agent created (different from the severity classification) is created in the MaritimeSeverityClassifier class. The class loads in the AStar training data and embedds it using all-MiniLM-L6-v2 as well and uses it as contextual data.

RAG Pipeline that integrates everything is in RiskAnalysisResult, it uses the corpus data setup with data_loader, the MaritimeClassifier for risk categorization, and the severity agent MaritimeSeverityClassifier for an output. It essentially is able to take in an article either via an URL or raw text and give a concise analysis.