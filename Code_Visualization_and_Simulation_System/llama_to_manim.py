import re
# import cv2
import ast
import torch
import numpy as np
from pathlib import Path
from tabulate import tabulate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


class llamaOutput:
    def __init__(self ):
        
        self.base_model = 'models/llama/llama-3.2-transformers-1b-instruct-v1'
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model,

            return_dict=True,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
            device_map="auto",  # Use Accelerate to handle devices
            trust_remote_code=True,
        )

        # Set pad_token_id if not already set
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        if self.model.config.pad_token_id is None:
            self.model.config.pad_token_id = self.model.config.eos_token_id

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            # model = 'llama-3.2-transformers-1b-instruct-v1',
            tokenizer=self.tokenizer,
            torch_dtype=torch.float16,
            device_map="auto",
        )


    def get_manim_code_from_input_code(self, code_parsed):
        """
        Generates Manim code for the provided parsed code with detailed illustrations,
        arrows, comments, and logical explanations.

        Args:
            code_parsed (str): The input code for which Manim visualizations are needed.

        Returns:
            str: Generated Manim code with enhanced illustrations and comments.
        """


        prompt = f"""You are a Manim code generation expert. Create Manim visualization code for the following Python code. The code must be directly runnable when saved to a .py file:

        {code_parsed}

        Generate ONLY the Python code that implements the visualization. The code must:
        1. Start with 'from manim import *'
        2. Define a single Scene class
        3. Include a construct method
        4. Use basic Manim elements like Text, Arrow, Rectangle, Comments in visualization
        5. Visualize the code execution flow
        6. Include NO explanations or markdown
        7. Don't give me input into solutions
        8. I don't input prompts in output, just give me what I want nothing more, nothing less!!! :/

        Example format for reference (replace with actual visualization code):
        from manim import *
        class CodeVisualization(Scene):
            def construct(self):
                # Your code here
                title = Text("Example")
                self.play(Write(title))
                
        DO NOT include any explanatory text, comments about the code, or markdown formatting. Return ONLY the runnable Python code."""


        try:
            prompt = prompt.strip()
            outputs = self.pipe(prompt, max_new_tokens=1500, do_sample=True, temperature=0.7,
                          top_p=0.95)

        except Exception as e:
            print(f"Primary prompt failed: {e}")
            outputs = self.pipe(prompt, max_new_tokens=1500, do_sample=True,temperature=0.7,
                          top_p=0.95)


        # Extract and validate output
        generated_text = outputs[0].get("generated_text", "")
        # if generated_text.startswith("```python") and generated_text.endswith("```"):
        #     return generated_text
        # else:
        #     return "Error: Output did not meet the expected format."
        return generated_text

        

    

    def parse_input(self,input_code):
        # Parse the code into an AST
        tree = ast.parse(input_code)

        # Pretty-print the AST structure
        # print(ast.dump(tree, indent=4))

        # Walk through the tree and find function definitions
        output = ""
        for node in ast.walk(tree):   #TODO: consider other cases too
            if isinstance(node, ast.FunctionDef):
                output.join(f"Function Name: {node.name}")
                output.join(f",Arguments: {[arg.arg for arg in node.args.args]}")
            else: 
                output= input_code
        return output
    
    

