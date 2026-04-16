from prompt_llm import get_llm_response

POSSIBLE_SUBJECTS = ["Maths Pure 1 (Paper 1)", "Maths Pure 3 (Paper 3)", "Maths Mechanics (Paper 4)", "Maths Probability & Statistics (Paper 5)", "Computer Science Advanced Theory (Paper 3)", "Computer Science Practical (Paper 4)", "Physics Further Mechanics, Fields and Particles (Paper 4)", "Physics Thermodynamics, Radiation, Oscillations and Cosmology (Paper 5)", "Physics Practical Skills II (Paper 6)"]

NOTE = """Maths Mechanics (Paper 4)
When sketching a parabola (quadratic), there are (up to) 6 points that should be clearly labelled; the y-axis intercept, the two x-axis intersections, the min/max, and the two extreme points between which the parabola is defined (i.e. the leftmost and rightmost defined points)."""

get_llm_response(NOTE)
