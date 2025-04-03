
class Course:
    # name: string indicating the name of the course. "ENG10", "MAT10", etc
    def __init__(self, name: str, students: list["Student"] = [], teacher: "Teacher" = None):
        """
        Initializes a Course object.
        """
        self.name = name
        self.students: list[Student] = students
        self.teachers: list[Teacher] = teacher
        self.sections: list[Section] = []

    def __repr__(self):
        return f"{self.name}"
    
    def create_section(self, students: list["Student"] = [], teacher: "Teacher" = None, block: str = "") -> "Section":
        """
        Creates a section for the course.
        """
        section = Section(self.name, students, teacher, block)
        self.sections.append(section)
        return section

class Section:
    # name: string indicating the name of the course. "ENG10", "MAT10", etc
    def __init__(self, name: str, students: list["Student"] = [], teacher: "Teacher" = None, block: str = ""):
        """
        Initializes a Course object.
        """
        self.name = name
        self.students: list[Student] = students
        self.teacher: Teacher = teacher
        self.block: str = block

    def __repr__(self):
        return f"{self.name}, block {self.block}, teacher {self.teacher.name}"
    
    def add_student(self, student: "Student"):
        self.students.append(student)

        student.add_section(self)    
    
    def add_teacher(self, teacher: "Teacher"):
        self.teacher = teacher
        teacher.add_section(self)

class Student:
    def __init__(self, name, required_courses: list[Course] = [], elective_courses: list[Course] = []):
        """
        Initializes a Student object.
        """
        self.name = name
        self.schedule: dict[str, Section] = {"A": None, "B": None, "C": None, "D": None, "E": None, "F": None, "G": None}
        self.required_courses: list[Course] = required_courses
        self.elective_courses: list[Course] = elective_courses

    def __str__(self):
        return f"Name: {self.name}"
    
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



class Teacher:
    def __init__(self, name):
        self.name = name
        self.schedule: dict[str, Section] = {"A": None, "B": None, "C": None, "D": None, "E": None, "F": None, "G": None}
        
        self.preferred_courses: list[Course] = []
        self.neutral_courses: list[Course] = [] # penalty for neutral courses
        self.unpreferred_courses: list[Course] = [] # larger penalty for unpreferred courses
        
        # TODO: variable penalties for different teachers
        
    def __str__(self):
        return f"Name: {self.name}. Teaching: {self.schedule}"
    
    def add_course(self, course: Course, likability: str = "preferred"):
        if likability == "preferred":
            self.preferred_courses.append(course)
        elif likability == "neutral":
            self.neutral_courses.append(course)
        elif likability == "unpreferred":
            self.unpreferred_courses.append(course)

    def add_section(self, section: Section):
        self.schedule[section.block] = section
    
