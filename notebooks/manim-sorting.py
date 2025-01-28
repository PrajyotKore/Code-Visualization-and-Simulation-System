from manim import *

class IllustratedBubbleSort(Scene):
    def construct(self):
        # Array to sort
        array = [7, 3, 5, 1, 4]

        # Background grid
        # grid = NumberPlane()
        # self.add(grid)

        # Boxed array elements
        boxes, text_objects = self.create_boxed_array(array)

        # Add elements to the scene
        self.play(*[Write(box) for box in boxes], *[Write(text) for text in text_objects])
        self.wait(1)

        # Step counter
        step_counter = Text("Step: 0", font_size=24).to_edge(UP + LEFT)
        self.add(step_counter)

        # Bubble Sort visualization
        n = len(array)
        step = 0
        for i in range(n):
            for j in range(0, n - i - 1):
                # Update step counter and comment
                step += 1
                self.update_step_counter(step_counter, step, f"Comparing indices {j} and {j+1}")

                # Highlight the two elements being compared and add arrows
                self.highlight_pair(boxes, j, j + 1)
                arrow1, arrow2 = self.add_arrows(boxes, j, j + 1)

                if array[j] > array[j + 1]:
                    # Update comment for swap
                    self.update_step_counter(step_counter, step, f"Swapping {array[j]} and {array[j+1]}")
                    # Swap elements in the array and visuals
                    array[j], array[j + 1] = array[j + 1], array[j]
                    self.swap_elements(boxes, text_objects, j, j + 1)

                # Remove arrows and unhighlight
                self.remove_arrows(arrow1, arrow2)
                self.unhighlight_pair(boxes, j, j + 1)

            # Mark the last sorted element as green
            self.mark_sorted(boxes, text_objects, n - i - 1, array[n - i - 1])

        # Mark all elements as sorted
        for k in range(n):
            self.mark_sorted(boxes, text_objects, k, array[k])

        self.update_step_counter(step_counter, step, "Sorting complete!")
        self.wait(2)

    def create_boxed_array(self, array):
        """Create a row of boxed elements for the array."""
        boxes = []
        text_objects = []
        for i, num in enumerate(array):
            box = Square(side_length=1).move_to(LEFT * 2 + RIGHT * i)
            text = Text(str(num), font_size=36).move_to(box.get_center())
            boxes.append(box)
            text_objects.append(text)
        return boxes, text_objects

    def highlight_pair(self, boxes, i, j):
        """Highlight the pair being compared."""
        self.play(
            boxes[i].animate.set_fill(YELLOW, opacity=0.5),
            boxes[j].animate.set_fill(YELLOW, opacity=0.5),
            run_time=0.5,
        )

    def unhighlight_pair(self, boxes, i, j):
        """Unhighlight the pair after comparison."""
        self.play(
            boxes[i].animate.set_fill(WHITE, opacity=0.5),
            boxes[j].animate.set_fill(WHITE, opacity=0.5),
            run_time=0.5,
        )

    def add_arrows(self, boxes, i, j):
        """Add arrows pointing to the pair being compared."""
        arrow1 = Arrow(start=UP, end=DOWN, buff=0.2).next_to(boxes[i], UP)
        arrow2 = Arrow(start=UP, end=DOWN, buff=0.2).next_to(boxes[j], UP)
        self.play(Create(arrow1), Create(arrow2), run_time=0.5)
        return arrow1, arrow2

    def remove_arrows(self, arrow1, arrow2):
        """Remove the arrows."""
        self.play(FadeOut(arrow1), FadeOut(arrow2), run_time=0.5)

    def swap_elements(self, boxes, text_objects, i, j):
        """Swap two elements in the visualization."""
        self.play(
            text_objects[i].animate.move_to(boxes[j].get_center()),
            text_objects[j].animate.move_to(boxes[i].get_center()),
            run_time=0.75,
        )
        self.play(
            boxes[i].animate.move_to(boxes[j].get_center()),
            boxes[j].animate.move_to(boxes[i].get_center()),
            run_time=0.75,
        )
        # Swap elements in the list
        boxes[i], boxes[j] = boxes[j], boxes[i]
        text_objects[i], text_objects[j] = text_objects[j], text_objects[i]

    def mark_sorted(self, boxes, text_objects, index, value):
        """Mark an element as sorted."""
        self.play(
            boxes[index].animate.set_fill(GREEN, opacity=0.5),
            text_objects[index].animate.set_color(GREEN),
            run_time=0.5,
        )

    def update_step_counter(self, step_counter, step, comment):
        """Update the step counter and add a comment."""
        new_text = Text(f"Step: {step}\n{comment}", font_size=24).to_edge(UP + LEFT)
        self.play(Transform(step_counter, new_text), run_time=0.5)
