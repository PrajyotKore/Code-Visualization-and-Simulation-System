from manim import *

class Visualization(Scene):
    def construct(self):
        # Initial array to be sorted
        arr = [38, 27, 43, 3, 9, 82, 10]
        n = len(arr)

        # Initialize Text objects for array elements
        text_elements = [Text(str(x)).scale(0.7) for x in arr]
        for i, text_obj in enumerate(text_elements):
            text_obj.move_to(LEFT * (n/2 - i) + DOWN*2.5)
        
        # Display the original array
        self.play(*[Write(text_obj) for text_obj in text_elements])
        self.wait(0.5)

        # Merge Sort function visualization
        def merge_sort_vis(arr, l, r, text_elements):
            if l < r:
                m = (l + r) // 2

                # Highlight the part of the array to be processed
                highlight_box_left = SurroundingRectangle(VGroup(*text_elements[l:m+1]), color=YELLOW, buff=0.1)
                highlight_box_right = SurroundingRectangle(VGroup(*text_elements[m+1:r+1]), color=BLUE, buff=0.1)
                self.play(Create(highlight_box_left), Create(highlight_box_right))
                self.wait(0.5)

                # Recursive calls for left and right halves
                merge_sort_vis(arr, l, m, text_elements)
                merge_sort_vis(arr, m + 1, r, text_elements)

                # Remove highlight boxes
                self.play(Uncreate(highlight_box_left), Uncreate(highlight_box_right))

                # Merge process with visualization
                merge_vis(arr, l, m, r, text_elements)

        def merge_vis(arr, l, m, r, text_elements):
            n1 = m - l + 1
            n2 = r - m
            L = arr[l:m+1]
            R = arr[m+1:r+1]

            # Highlight the left and right arrays being merged
            highlight_box_left = SurroundingRectangle(VGroup(*text_elements[l:m+1]), color=YELLOW, buff=0.1)
            highlight_box_right = SurroundingRectangle(VGroup(*text_elements[m+1:r+1]), color=BLUE, buff=0.1)
            self.play(Create(highlight_box_left), Create(highlight_box_right))
            self.wait(0.5)
            
            # Create temp text elements for comparison and merging
            temp_elements = [Text(str(x)).scale(0.7) for x in arr[l:r+1]]
            for i, temp_obj in enumerate(temp_elements):
                temp_obj.move_to(LEFT * ((r-l+1)/2 - i) + DOWN*1.0)
            
            
            self.play(*[TransformFromCopy(text_elements[l+i], temp_elements[i]) for i in range(r-l+1) ])


            i = 0
            j = 0
            k = l
            
            # Perform merging
            while i < n1 and j < n2:
                
                # Highlight elements being compared
                compare_arrow_l = Arrow(temp_elements[i].get_top(), temp_elements[i].get_top()+UP*0.5, color=YELLOW)
                compare_arrow_r = Arrow(temp_elements[n1+j].get_top(), temp_elements[n1+j].get_top()+UP*0.5, color=BLUE)
                self.play(Create(compare_arrow_l), Create(compare_arrow_r))
                self.wait(0.3)
                if L[i] <= R[j]:
                    arr[k] = L[i]
                    # Move the element to its sorted place
                    self.play(Transform(temp_elements[i].copy(), text_elements[k]))
                    i += 1
                else:
                    arr[k] = R[j]
                    # Move the element to its sorted place
                    self.play(Transform(temp_elements[n1+j].copy(), text_elements[k]))
                    j += 1
                self.play(Uncreate(compare_arrow_l), Uncreate(compare_arrow_r))
                k += 1
                self.wait(0.3)
            
            # Copy remaining elements from left sublist
            while i < n1:
                arr[k] = L[i]
                self.play(Transform(temp_elements[i].copy(), text_elements[k]))
                i += 1
                k += 1
                self.wait(0.2)

            # Copy remaining elements from right sublist
            while j < n2:
                arr[k] = R[j]
                self.play(Transform(temp_elements[n1+j].copy(), text_elements[k]))
                j += 1
                k += 1
                self.wait(0.2)

            # Remove highlights and temp array
            self.play(Uncreate(highlight_box_left), Uncreate(highlight_box_right),
                         *[FadeOut(temp_obj) for temp_obj in temp_elements]
                    )
            self.wait(0.5)

        # Start the merge sort visualization
        merge_sort_vis(arr, 0, n - 1, text_elements)

        # Final sorted array
        self.wait(1)
        self.play(*[text_obj.animate.set_color(GREEN) for text_obj in text_elements])
        self.wait(2)