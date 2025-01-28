
from Code_Visualization_and_Simulation_System import llama_to_manim, run_manim_code

if __name__ == "__main__":

    input_code ="""def bubbleSort(arr):
    n = len(arr)
    
    # Traverse through all array elements
    for i in range(n):
        swapped = False

        # Last i elements are already in place              
        for j in range(0, n-i-1):

            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if (swapped == False):
            break"""
    
    ## 
    llamaManim = llama_to_manim.llamaOutput() 
    parsedInput = llamaManim.parse_input(input_code)
    print("Generating Manim Scripts...")
    manimScript = llamaManim.get_manim_code_from_input_code(parsedInput)
    # print(manimScript)
    with open("manim_script.txt", "w") as text_file:
        text_file.write(manimScript)
    extract_python_manim_code_from_output = run_manim_code.extract_manim_code(manimScript)
    # print(extract_python_manim_code_from_output)
    print('Generating Illustration....')                
    run_manim_code.save_and_run_manim_script(manimScript)
    print('Generation Complete!! :)')
    


