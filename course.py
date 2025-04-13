import math
from params import *
# class Block:
#     def __init__(self, name: str, start_time: str, end_time: str, sections: list["Section"] = []):
#         """
#         Initializes a Block object.
#         """
#         self.name = name
#         self.start_time = start_time
#         self.end_time = end_time
#         self.sections: list[Section] = sections

#     def __str__(self):
#         return f"{self.name} ({self.start_time} - {self.end_time})"
class Course:
    # name: string indicating the name of the course. "ENG10", "MAT10", etc
    def __init__(self, name: str, students: list["Student"] = None, active_teachers: "Teacher" = None):
        """
        Initializes a Course object.
        """
        self.name = name
        self.students: list[Student] = students if students is not None else []
        self.active_teachers: list[Teacher] = active_teachers if active_teachers is not None else [] # contains only the teachers that are currently teaching this course
        self.finished_assigning_teachers: bool = False # whether all sections of this course have been assigned to a teacher or not

        # these three lists contain all teachers that CAN teach this course, regardless of whether they are currently teaching it or not
        self.preferred_teachers: list[Teacher] = [] # teachers that are preferred for this course
        self.neutral_teachers: list[Teacher] = []
        self.unpreferred_teachers: list[Teacher] = []

        self.sections: list[Section] = []

    def __repr__(self):
        return f"{self.name}"
    
    def create_section(self, students: list["Student"] = [], teacher: "Teacher" = None, block: int = -1) -> "Section":
        """
        Creates a section for the course.
        """
        section = Section(self.name, students, teacher, block)
        self.sections.append(section)
        teacher.add_section(section)
        return section
    
    def get_course_desirability_teaching(self) -> int:
        """
        Returns the desirability of the course based on the number of teachers who prefer it.
        """
        d = len(self.preferred_teachers)*2 + len(self.neutral_teachers)
        return d
    
    def estimated_number_of_sections(self) -> int:
        """
        Returns the estimated number of sections for this course based on the number of students and teachers.
        """
        return math.ceil(len(self.students)/IDEAL_CLASS_SIZE)
    
    def get_best_teacher(self) -> "Teacher":
        """
        Returns the best teacher for this course based on the number of preferred teachers.
        """
        best_teacher = None
        most_picky = -1
        for teacher in self.preferred_teachers:
            if not teacher.has_full_schedule() and teacher.get_pickiness_level() > most_picky:
                most_picky = teacher.get_pickiness_level()
                best_teacher = teacher
        if best_teacher is None:
            for teacher in self.neutral_teachers:
                if not teacher.has_full_schedule() and teacher.get_pickiness_level() > most_picky:
                    most_picky = teacher.get_pickiness_level()
                    best_teacher = teacher
        return best_teacher
    
    def get_unfilled_sections(self) -> list["Section"]:
        """
        Returns the sections that are not filled yet.
        """
        return [section for section in self.sections if section.is_full() == False]

class Section:
    # name: string indicating the name of the course. "ENG10", "MAT10", etc
    def __init__(self, name: str, students: list["Student"] = None, teacher: "Teacher" = None, block: int = -1):
        """
        Initializes a Course object.
        """
        self.name = name
        self.students: list[Student] = students if students is not None else []
        self.teacher: Teacher = teacher
        self.block: str = block
        
        if teacher is not None:
            teacher.add_section(self)

        for student in students:
            student.add_section(self)


    def __repr__(self):
        return f"{self.name}, block {self.block}"
    
    def add_student(self, student: "Student"):
        self.students.append(student)
        student.add_section(self)    
    
    def add_teacher(self, teacher: "Teacher"):
        self.teacher = teacher
        teacher.add_section(self)
    
    def is_full(self):
        """
        Returns whether the section is full or not.
        """
        return len(self.students) >= MAX_CLASS_SIZE
class Student:
    def __init__(self, name, required_courses: list[Course] = None, elective_courses: list[Course] = None):
        """
        Initializes a Student object.
        """
        self.name = name
        self.schedule: dict[int, Section] = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        self.required_courses: list[Course] = required_courses if required_courses is not None else []
        self.elective_courses: list[Course] = elective_courses if elective_courses is not None else []
        for course in required_courses:
            course.students.append(self)
        for course in elective_courses:
            course.students.append(self)

    def __str__(self):
        return f"Name: {self.name}"
    
    def __repr__(self):
        return f"{self.name}"
    def add_course(self, course: Course, is_required=True):
        if is_required:
            self.required_courses.append(course)
        else:
            self.elective_courses.append(course)
            
    def add_section(self, section: Section):        
        if section.name not in self.required_courses and section.name not in self.elective_courses:
            raise ValueError(f"Section {section.name} is not a valid course for student {self.name}.")
        self.schedule[section.block] = section

    def get_all_courses(self) -> list[Course]:
        """
        Returns a list of all courses the student is enrolled in.
        """
        return self.required_courses + self.elective_courses

    def get_flexibility(self):
        """
        Returns the flexibility of the student.

        Sum of the number of total sections for each course in their schedule that hasn't already been placed.
        """
        f = 0
        for course in self.get_all_courses():
            if course.name in [section.name for section in self.schedule.values() if section is not None]:
                continue
            f += len(course.get_unfilled_sections())
        return f

class Teacher:
    def __init__(self, name, test: list[Course] = None, preferred_courses: list[Course] = None, neutral_courses: list[Course] = None, unpreferred_courses: list[Course] = None):
        """
        Initializes a Teacher object.
        """

        self.name = name
        self.schedule: dict[int, Section] = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        
        self.preferred_courses: list[Course] = preferred_courses if preferred_courses is not None else list()
        self.neutral_courses: list[Course] = neutral_courses if neutral_courses is not None else list() # penalty for neutral courses        self.unpreferred_courses: list[Course] = [] if unpreferred_courses is None else unpreferred_courses # larger penalty for unpreferred courses
        self.unpreferred_courses: list[Course] = unpreferred_courses if unpreferred_courses is not None else list() # larger penalty for unpreferred courses
        
        self.teaching_blocks: set[int] = set() # blocks that are already taken by the teacher

        for course in self.preferred_courses:
            course.preferred_teachers.append(self)
    
        for course in self.neutral_courses:
            course.neutral_teachers.append(self)

        for course in self.unpreferred_courses:
            course.unpreferred_teachers.append(self)

        # TODO: variable penalties for different teachers
        
    def __str__(self):
        return f"Name: {self.name}. Teaching: {self.schedule}"
    
    def __repr__(self):
        return self.__str__()
    
    def add_course(self, course: Course, likability: str = "preferred"):
        if likability == "preferred":
            self.preferred_courses.append(course)
            course.preferred_teachers.append(self)
        elif likability == "neutral":
            self.neutral_courses.append(course)
            course.neutral_teachers.append(self)
        elif likability == "unpreferred":
            self.unpreferred_courses.append(course)
            course.unpreferred_teachers.append(self)

    def add_section(self, section: Section):
        """
        Adds a section to the teacher's schedule.
        If the section is already in the schedule, it will be replaced.

        Args:
            section (Section): _description_
        """
        self.schedule[section.block] = section
        self.teaching_blocks.add(section.block)

    def get_pickiness_level(self) -> int:
        """
        Returns the pickiness level of the teacher. 
        #TODO make this Sum of the product of number of sections and the pickiness level of each course.
        """
        pickiness = 0
        for course in self.preferred_courses:
            pickiness += course.estimated_number_of_sections()
        for course in self.unpreferred_courses:
            pickiness += course.estimated_number_of_sections()

        # account for the classes they are already teaching
        for section in self.schedule.values():
            if section is not None:
                if section.name in self.preferred_courses or section.name in self.unpreferred_courses:
                    pickiness -= 1
        return pickiness
    
    def has_full_schedule(self) -> bool:
        """
        Returns whether the teacher has a full schedule or not.
        """
        return len(self.teaching_blocks) >= MAX_CLASSES_PER_TEACHER
