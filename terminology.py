import re

AI_DICTIONARY = {
    "llm": {
        "term": "LLM (Large Language Model)",
        "definition": "A type of AI model trained on vast amounts of text data to understand and generate human-like language.",
        "example": "ChatGPT, Claude, and Gemini are all Large Language Models.",
        "importance": "They serve as the foundation for modern conversational AI and text generation."
    },
    "transformer": {
        "term": "Transformer",
        "definition": "A neural network architecture that learns context and meaning by tracking relationships in sequential data.",
        "example": "The 'T' in ChatGPT stands for Transformer.",
        "importance": "It revolutionized NLP by allowing models to process entire sentences at once rather than word-by-word."
    },
    "diffusion": {
        "term": "Diffusion Model",
        "definition": "A generative AI model that learns to create data (like images) by reversing a process of adding noise to it.",
        "example": "Midjourney and DALL-E use diffusion to generate images from text prompts.",
        "importance": "They represent the current state-of-the-art for generating highly realistic images and video."
    },
    "fine-tuning": {
        "term": "Fine-Tuning",
        "definition": "Taking a pre-trained model and training it further on a smaller, specific dataset to specialize its knowledge.",
        "example": "Taking a general coding AI and fine-tuning it exclusively on Python code.",
        "importance": "It allows developers to create specialized, highly accurate AI without spending millions training from scratch."
    },
    "prompt engineering": {
        "term": "Prompt Engineering",
        "definition": "The practice of designing and refining the text inputs given to an AI to produce optimal outputs.",
        "example": "Asking an AI to 'Think step by step' before answering a math problem.",
        "importance": "It significantly improves the reliability and quality of AI responses."
    },
    "inference": {
        "term": "Inference",
        "definition": "The phase where a trained AI model is put to work making predictions or generating text based on new data.",
        "example": "When you send a message to ChatGPT and it replies, that calculation is 'inference'.",
        "importance": "This is where the computational cost shifts from training the model to actually running it for users."
    },
    "multimodal": {
        "term": "Multimodal AI",
        "definition": "AI capable of understanding and generating multiple data types, such as text, images, and audio simultaneously.",
        "example": "ChatGPT looking at a photo of your fridge and telling you what you can cook.",
        "importance": "It bridges the gap between different types of sensory inputs, making AI much more capable."
    },
    "rag": {
        "term": "RAG (Retrieval-Augmented Generation)",
        "definition": "A technique that grounds an AI's response by having it search a database for facts before answering.",
        "example": "A customer support bot searching your company's private handbook before replying.",
        "importance": "It dramatically reduces AI hallucinations (making things up) and allows AI to access private data."
    },
    "embedding": {
        "term": "Embedding",
        "definition": "A way of representing words, images, or concepts as numbers so computers can understand their relationships.",
        "example": "Translating the word 'King' into a list of 1,000 numbers that capture its meaning.",
        "importance": "Embeddings are the fundamental building block that allows AI to do math with human concepts."
    },
    "token": {
        "term": "Token",
        "definition": "The basic unit of data an AI processes. A token can be a word, part of a word, or just a few characters.",
        "example": "The word 'hamburger' might be split into three tokens: 'ham', 'bur', 'ger'.",
        "importance": "AI pricing and memory limits are based on how many tokens they process."
    },
    "vector database": {
        "term": "Vector Database",
        "definition": "A specialized database designed to store and search embeddings (data represented as numbers) very quickly.",
        "example": "Pinecone or Milvus storing millions of company documents for a RAG system to search.",
        "importance": "It enables AI to perform 'semantic search' (searching by meaning rather than exact keywords)."
    },
    "agi": {
        "term": "AGI (Artificial General Intelligence)",
        "definition": "A hypothetical AI system that can understand, learn, and apply knowledge across a wide range of tasks at a human or superhuman level.",
        "example": "An AI that can invent new physics theories, write a bestselling novel, and run a company.",
        "importance": "It is considered the ultimate goal of AI research and would fundamentally change human society."
    },
    "ai": {
        "term": "AI (Artificial Intelligence)",
        "definition": "The simulation of human intelligence processes by machines, especially computer systems.",
        "example": "Virtual assistants like Siri and Alexa are examples of AI.",
        "importance": "It is the overarching field that encompasses all smart machine technologies."
    },
    "machine learning": {
        "term": "Machine Learning (ML)",
        "definition": "A subset of AI that allows systems to automatically learn and improve from experience without being explicitly programmed.",
        "example": "Netflix recommending a movie based on your watch history uses machine learning.",
        "importance": "It shifted AI from rules-based programming to data-driven learning."
    },
    "deep learning": {
        "term": "Deep Learning",
        "definition": "A type of machine learning based on artificial neural networks with multiple layers of processing.",
        "example": "Facial recognition systems on modern smartphones rely on deep learning.",
        "importance": "It is responsible for the massive leaps in computer vision and natural language processing in recent years."
    },
    "nlp": {
        "term": "NLP (Natural Language Processing)",
        "definition": "A branch of AI that gives computers the ability to understand text and spoken words in much the same way human beings can.",
        "example": "This very application summarizing a news article is an example of NLP.",
        "importance": "It bridges the communication gap between humans and computers."
    },
    "algorithm": {
        "term": "Algorithm",
        "definition": "A set of mathematical instructions or rules given to an AI to help it learn from data and make decisions.",
        "example": "YouTube's recommendation algorithm decides which video to show you next.",
        "importance": "Algorithms are the core logic engines driving all software and AI systems."
    },
    "neural network": {
        "term": "Neural Network",
        "definition": "A computing system inspired by the biological neural networks that constitute animal brains.",
        "example": "An image classification system identifying cats vs dogs uses a neural network.",
        "importance": "It forms the foundation of deep learning and complex pattern recognition."
    },
    "dataset": {
        "term": "Dataset",
        "definition": "A large collection of data used to train, test, or evaluate an AI model.",
        "example": "Wikipedia and Reddit were used as datasets to train Large Language Models.",
        "importance": "High-quality datasets are often more critical to an AI's success than the algorithm itself."
    }
}

def explain_terminology(text):
    """
    Automatically detect technical AI terms inside the article and explain them.
    """
    if not text:
        return []
        
    text_lower = text.lower()
    detected_terms = []
    
    for key, data in AI_DICTIONARY.items():
        # Check for whole word matches to avoid partial matches (e.g. 'rag' inside 'courage')
        # \b is word boundary
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text_lower):
            detected_terms.append(data)
            
    return detected_terms
