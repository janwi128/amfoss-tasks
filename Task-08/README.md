# APPROACH:
I started this task by breaking it down into smaller steps.
first, i learned to use OPenCV for segmentation - I used OpenCV to detect the block area and calculate its centroid.

for every detected block , I calculated the average colour.
After analyzing all tiles, I stitched them together in the right order.

the final output is treasure_map.png which shows :
Dots = blocks centers,colored by their average colour.
lines = the path from one block to the next.
"x"markers = teleport/blank tiles that are not joined in the path.
To create this final image(treasure path) i learned to use pillow.

Along the way i had challenges-like initially detecting multiple contours inside a block which gave wrong centers.
I debuuged that by focusing only on largest contour. 

What i really learned in this task was how to approach a computer vision task step by step.
I practiced algorithmic thinking ,debugging and using OpenCV tools in a real project. 
This task gave me a lot of new learnings.
