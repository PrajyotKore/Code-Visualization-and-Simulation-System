import os
import chromadb
from google import genai
import google.generativeai as genai
from google.api_core import retry
from IPython.display import Markdown
from chromadb import Documents, EmbeddingFunction, Embeddings
import atexit


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    raise ValueError("Please set GOOGLE_API_KEY environment variable")



class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, document_mode=True):
        self.document_mode = document_mode

    def __call__(self, input: Documents) -> Embeddings:
        task = "retrieval_document" if self.document_mode else "retrieval_query"
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=task
        )
        return response["embedding"]

class ManimFromRAG:
    def __init__(self, manim_dir):
        # Load documents
        self.documents = []
        for doc in os.listdir(manim_dir):
            with open(os.path.join(manim_dir, doc), "r", encoding="utf-8") as file:
                self.documents.append(file.read())
        
        # Setup ChromaDB
        self.chroma_client = chromadb.Client()
        self.embed_fn = GeminiEmbeddingFunction()
        self.collection = self.chroma_client.create_collection(
            name="manim_collection",
            embedding_function=self.embed_fn
        )

    def index_documents(self):
        if self.documents:
            self.collection.add(
                documents=self.documents,
                ids=[str(i) for i in range(len(self.documents))]
            )
            return True
        return False

    def generate_manim(self, code_snippet):
        # Query similar documents
        query=f"""
        {code_snippet}
        Guidlines:
        1. make sure that code to be runnable directly and try to be more creative,
        2. add explainations, comments in texts and arrows in animation
        3. try to make, creative, consice visualization
        4. animation video can be big
        5. keep output resolution of animation to 720 pixels, hence, keep content of animation relevant to it
        6. No overlapping texts or objects in animation
        
        """
        
        results = self.collection.query(query_texts=[query], n_results=1)
        reference = results["documents"][0][0]
        
        # Generate prompt
        prompt =f"""Consider you as Manim Expert and I want you to create code out using both Question and Passage.
            Guidelines
            1. Make the code such that animations or visuilization created by the code, will be illustrative enough
            2. Response, should not contain anything but direct runnable code
            3. add illustrative comments and explainations in visualization or animation 
            4. try to creat more creative illustrations 
            5. don't give defective code
            6. if input is too large, consider breaking it into smaller chunks ans do the animation
            7. dont use anything related latex
            8. Give me complete animation, time is no contraint,  but animation should show whole process
            9. also, be mindful about the comment, explainations and their positions
            10. consider the Class name to be Visualization
            If the passage is irrelevant to the answer, you may ignore it.

            QUESTION: {query}
            PASSAGE: {reference}
            """
        
        # Generate code using Gemini
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text

# def main():
#     # Directory containing Manim documentation
#     manim_dir = r"C:\Users\Asus\Desktop\Prajyot\Code Visualization and Simulation System\data\raw\Manim Docs\Manim Docs"
    
#     # Initialize and index documents
#     rag = ManimFromRAG(manim_dir)
#     rag.index_documents()
    
#     # Example code to visualize
#     code = """
#     def selection_sort(arr):
#         n = len(arr)
#         for i in range(n - 1):
#             min_idx = i
#             for j in range(i + 1, n):
#                 if arr[j] < arr[min_idx]:
#                     min_idx = j
#             arr[i], arr[min_idx] = arr[min_idx], arr[i]
#     """
    
#     # Generate Manim visualization
#     result = rag.generate_manim(code)
#     print(result)

# if __name__ == "__main__":
#     main()