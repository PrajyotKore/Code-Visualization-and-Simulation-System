from Code_Visualization_and_Simulation_System.manim_code_generation_from_RAG import ManimFromRAG
from Code_Visualization_and_Simulation_System.run_manim_code import save_and_run_manim_script, extract_manim_code

def recursively_run_manim_script(rag, code, max_retries=3, attempt=1):
    """
    Recursively generates, saves, and runs Manim scripts, retrying if errors occur.

    Args:
        rag (ManimFromRAG): The RAG object for Manim code generation.
        code (str): The input code to visualize.
        max_retries (int): Maximum number of retry attempts.
        attempt (int): Current retry attempt number.

    Returns:
        dict: The final response from save_and_run_manim_script, including output or error.
    """
    # Step 1: Generate Manim visualization
    print(f"Attempt {attempt}: Generating Manim script...")
    result = rag.generate_manim(code)

    # Step 2: Extract Manim code from the generated result
    manim_code = extract_manim_code(result)

    # Step 3: Save and run the Manim code
    response = save_and_run_manim_script(manim_code)

    # Step 4: Handle errors and retry if necessary
    if response["error"]:
        print(f"Error encountered on attempt {attempt}: {response['error']}")
        
        # Check if the maximum retry limit h        as been reached
        if attempt >= max_retries:
            print("Max retries reached. Returning the final error.")
            return response
        
        # Create a secondary prompt with the failed Manim code and error message
        secondary_prompt = (
            f"The following Manim code failed to run:\n\n{manim_code}\n\n"
            f"Error message:\n{response['error']}"
        )

        # Recursively call the function with the secondary prompt
        return recursively_run_manim_script(rag, code, max_retries, attempt + 1)

    # If successful, return the response
    print(f"Animation successfully created on attempt {attempt}!")
    return response


if __name__ == "__main__":
    # Directory containing Manim documentation
    manim_dir = r"C:\Users\Asus\Desktop\Prajyot\Code Visualization and Simulation System\data\raw\Manim Docs\Manim Docs"
    
    # Initialize and index documents
    rag = ManimFromRAG(manim_dir)
    rag.index_documents()
    
    # Example code to visualize
    # code = """
    # def selection_sort(arr):
    #     n = len(arr)
    #     for i in range(n - 1):
    #         min_idx = i
    #         for j in range(i + 1, n):
    #             if arr[j] < arr[min_idx]:
    #                 min_idx = j
    #         arr[i], arr[min_idx] = arr[min_idx], arr[i]
    # """
    input_path = r"C:\Users\Asus\Desktop\Prajyot\Code Visualization and Simulation System\data\raw\sample_input_code.txt"
    with open(input_path, "r", encoding="utf-8") as file:
        code = file 
    code = "Show how Convolution happens in CNN, without image consider random image matrix,  "
    # Recursively try to generate, save, and run the Manim script
    final_response = recursively_run_manim_script(rag, code)    

    # Print the final output or error
    if final_response["error"]:
        print("Final error:", final_response["error"])
    else:
        print("Final output:\n", final_response["output"])
