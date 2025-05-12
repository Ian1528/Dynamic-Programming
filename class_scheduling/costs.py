from course import *

def cost_of_final_schedules_from_courses(courses: list[Course]) -> int:
    """Calculates the cost of the final schedules based on the number of students in each section and the number of sections.
    
    Returns:
        int: The total cost of the final schedules.
    """
    total_cost = 0
    student_preference_penalty = 0
    infeasible_penalty = 0

    teacher_preference_penalty = 0
    lopsided_distribution_penalty = 0

    students: set[Student] = set()
    for course in courses:
        for section in course.sections:
            for student in section.students:
                students.add(student)
    teachers: set[Teacher] = set()
    for course in courses:
        for section in course.sections:
            teachers.add(section.teacher)
    
    for student in students:
        schedule_courses = {section.course for section in student.schedule.values() if section is not None}
        if len(set(schedule_courses)) < len(schedule_courses):
            print("Student enrolled mutliple times in the same course!")
        # check that all students have their required courses
        for course in student.course_requests:
            course_found = False
            for i in range(len(course)):
                if course[i] in schedule_courses:
                    course_found = True
                    student_preference_penalty += i
                    break
            if not course_found:
                print(f"Student {student.name} is missing course {course}.")
                infeasible_penalty += 100
                # return math.inf

    for course in courses:
        num_sections = len(course.sections)

        # calculate mean and standard deviation of students per sections
        if num_sections > 0:
            students_per_section = [len(section.students) for section in course.sections]
            mean_students = np.mean(students_per_section)
            std_students = np.std(students_per_section)

            if std_students > 1 and std_students < 1.75:
                lopsided_distribution_penalty += 5
            elif std_students >= 1.75 and std_students < 2.5:
                lopsided_distribution_penalty += 10
            elif std_students > 2.5:
                lopsided_distribution_penalty += 50
            print("Standard deviation of course", course.name, ":", std_students)
            print("Class sizes")
            for section in course.sections:
                print(section, len(section.students))

            print("***\n\n\n")
    total_cost = student_preference_penalty + infeasible_penalty + lopsided_distribution_penalty
    return total_cost