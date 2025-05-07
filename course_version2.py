import math
import random
import numpy as np
from params import *

class Course:
    # name: string indicating the name of the course. "ENG10", "MAT10", etc
    def __init__(self, name: str, students: list["Student"] = None, active_teachers: "Teacher" = None, is_elective: bool = False):
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

        self.conflicting_courses: set[Course] = set() # courses that are in conflict with this course.
        self.non_conflicting_courses: set[Course] = set() # courses that are not in conflict with this course.

        self.is_elective: bool = is_elective # whether the course is an elective or not
    def __repr__(self):
        return f"{self.name}"
    

    def create_section(self, students: list["Student"] = None, teacher: "Teacher" = None, block: int = -1) -> "Section":
        """
        Creates and returns section for the course.
        """
        section = Section(self.name, students, teacher, block, self)
        self.sections.append(section)
        self.active_teachers.append(teacher)

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
        if best_teacher is None:
            for teacher in self.unpreferred_teachers:
                if not teacher.has_full_schedule() and teacher.get_pickiness_level() > most_picky:
                    most_picky = teacher.get_pickiness_level()
                    best_teacher = teacher
        return best_teacher
    
    def get_unfilled_sections(self) -> list["Section"]:
        """
        Returns the sections that are not filled yet.
        """
        return [section for section in self.sections if section.is_full() == False]
    def get_section(self, block: int) -> "Section":
        """
        Returns the section for the course in the given block.
        """
        for section in self.sections:
            if section.block == block:
                return section
        raise Exception("No section found for this course in this block!")
    def reset_students_in_sections(self) -> None:
        """
        Resets the sections of the course.
        """
        for section in self.sections:
            section.students = []

    def reset_sections(self) -> None:
        """
        Resets the teachers of the course.
        """
        self.sections = []
        self.active_teachers = [] # contains only the teachers that are currently teaching this course
        self.finished_assigning_teachers = False # whether all sections of this course have been assigned to a teacher or not

    def add_student(self, student: "Student") -> None:
        """
        Adds a student to the course.
        """
        self.students.append(student)

    def remove_student(self, student: "Student") -> None:
        """
        Removes a student from the course.
        """
        if student in self.students:
            self.students.remove(student)
        else:
            raise Exception("Student not found in course!")
class Section:
    # name: string indicating the name of the course. "ENG10", "MAT10", etc
    def __init__(self, name: str, students: list["Student"] = None, teacher: "Teacher" = None, block: int = -1, course: Course = None):
        """
        Initializes a Course object.
        """
        self.name = name
        self.students: list[Student] = students if students is not None else []
        self.teacher: Teacher = teacher
        self.block: int = block
        self.course: Course = course # course that this section belongs to
        
        if self.teacher is not None:
            teacher.add_section(self)

        for student in self.students:
            student.add_section(self)


    def __repr__(self):
        return f"{self.name} - {self.block} with n={len(self.students)} "
    
    def add_student(self, student: "Student"):
        if student in self.students:
            return
            # raise Exception("Student is already in this section!")
        self.students.append(student)
        student.add_section(self)    
    
    def remove_student(self, student: "Student"):
        if student not in self.students:
            raise Exception("Student is not in this section!")
        self.students.remove(student)
        student.schedule[self.block] = None
        
    def add_teacher(self, teacher: "Teacher"):
        self.teacher = teacher
        teacher.add_section(self)
    
    def is_full(self):
        """
        Returns whether the section is full or not.
        """
        return len(self.students) >= MAX_CLASS_SIZE
class Student:
    def __init__(self, name, course_requests: list[list[Course]] = None, grade: int = None):
        """
        Initializes a Student object.
        """
        self.name = name
        self.schedule: dict[int, Section] = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        self.course_requests: list[list[Course]] = course_requests if course_requests is not None else []
        self.grade: int = grade
        # start by giving every student their first choice
        for course_rankings in self.course_requests:
            course_rankings[0].add_student(self)

    def __str__(self):
        return f"Name: {self.name}"
    
    def __repr__(self):
        return f"{self.name}"
    
    def reset_schedule(self):
        """
        Resets the schedule of the student.
        """
        self.schedule = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
    def add_single_course(self, course: Course) -> None:
        """
        Adds a course to the course requests of the student. 
        If another course from the same department is already in the course requests, it will be replaced.

        Args:
            course (Course): the course to add

        Raises:
            Exception: if the course is already in the course requests
        """
        self.course_requests.append([course])
    def replace_single_course(self, old_course: Course, new_course: Course) -> None:
        """
        Replaces a course in the course requests of the student. 
        If another course from the same department is already in the course requests, it will be replaced.

        Args:
            old_course (Course): the course to replace
            new_course (Course): the course to add

        Raises:
            Exception: if the course is already in the course requests
        """
        for course_rankings in self.course_requests:
            try:
                index_of_old_course = course_rankings.index(old_course)
                course_rankings[index_of_old_course] = new_course
                return
            except ValueError:
                pass
        raise Exception("Course not found in course requests!")
    def add_course_preferences(self, course_preferences: list[Course]) -> None:
        """
        Adds a list of course preferences to the course requests of the student. 
        If another course from the same department is already in the course requests, it will be replaced.

        Args:
            course_preferences (list[Course]): the list of courses to add

        Raises:
            Exception: if the course is already in the course requests
        """
        self.course_requests.append(course_preferences)
            
    def add_section(self, section: Section):
        if self.schedule[section.block] is not None:
            raise Exception("Block already taken!")     
        self.schedule[section.block] = section

    def get_all_first_choice_courses(self) -> list[Course]:
        """
        Returns a list of all first choice courses the student is enrolled in.
        """
        return [course_preferences[0] for course_preferences in self.course_requests] # only the first course in the list is considered

    def get_flexibility(self):
        """
        Returns the flexibility of the student.

        Sum of the number of total sections for each course in their schedule that hasn't already been placed.
        """
        f = 0
        for course in self.get_all_first_choice_courses():
            if course.name in [section.name for section in self.schedule.values() if section is not None]:
                continue
            f += len(course.get_unfilled_sections())
        return f
    
    def get_course_section(self, course: Course) -> Section |  None:
        """
        Returns the section for the course in the student's schedule. None if the course is not in the schedule.
        """
        for section in self.schedule.values():
            if section is not None and section.course == course:
                return section
        return None
    def get_unassigned_courses(self) -> list[Course]:
        """
        Returns a list of all courses the student is enrolled in that are not assigned to a section yet.
        """
        return [course for course in self.get_all_first_choice_courses() if course.name not in [section.name for section in self.schedule.values() if section is not None]]
    
        
    def get_available_sections_with_saturation(self, current_course: Course, current_section: Section | None = None) -> dict[Section, int]:
        """
        Returns a list of all sections for a course that the student can be assigned to.
        """
        available_sections: list[Section] = []
        for section in current_course.sections:
            if self.schedule[section.block] is None:
                available_sections.append(section)
        if current_section is not None:
            available_sections.append(current_section)

        sections_saturations = {section: 1 for section in available_sections}
        available_sections_blocks: set[int] = set([section.block for section in available_sections])
        for course in self.get_unassigned_courses():
            if course == current_course:
                continue
            for section in course.get_unfilled_sections():
                if section.block in available_sections_blocks and not section.is_full():
                    corresponding_sections_to_block = [s for s in available_sections if s.block == section.block]

                    for s in corresponding_sections_to_block:
                        sections_saturations[s] += 1
        
        # normalize the saturation weights
        saturation_weights = np.array(list(sections_saturations.values()))

        saturation_weights = saturation_weights / np.sum(saturation_weights)

        sections_saturations = {section: int(saturation_weights[i]*100) for i, section in enumerate(sections_saturations.keys())}
        
        return sections_saturations
    
    def reassign_block(self, block: int, blocks_to_avoid: list[int], layer_num: int) -> bool:
        """
        If the block is empty, the function returns True. Otherwise, it attempts to free up the block by reassiging whatever class is currently in the block. 
        
        Returns True if successful, False otherwise. 
        Recursively calls itself until it finds a block that is empty or determines that it's infeasible.

        """
        if len(blocks_to_avoid) >= len(self.schedule):
            return False
        old_section = self.schedule[block]

        if old_section is None:
            return True
        
        other_sections = old_section.course.get_unfilled_sections()

    
        candidate_sections: dict[Section, int] = {}
        for section in other_sections:
            if section.block not in blocks_to_avoid:
                if self.schedule[section.block] is None:
                    candidate_sections[section] = len(section.students)

        if len(candidate_sections) > 0:
            # pick the smallest section to switch into
            best_section = min(candidate_sections, key=candidate_sections.get)
            # remove from the old section
            old_section.remove_student(self)
            # add to the new section
            best_section.add_student(self)

            if self.name == "Student 38 Grade 12" and old_section.course.name == "MAT50":
                print(f"Reassigned {self.name} from {old_section} to {best_section}")
            return True
        
        else:
            other_sections_sorted = sorted(other_sections, key=lambda x: len(x.students))
            for section in other_sections_sorted:
                if section.block in blocks_to_avoid:
                    continue
                reassigned = self.reassign_block(section.block, blocks_to_avoid + [section.block], layer_num+1)
                if reassigned:
                    # remove from the old section
                    # add to the new section
                    if self.name == "Student 38 Grade 12" and section.course.name == "MAT50":
                        print(f"Reassigned {self.name} from {old_section} to {section}")

                    old_section.remove_student(self)
                    section.add_student(self)
                    return True
            # if we get here, it means we couldn't find a block to reassign to

            return False
class Teacher:
    def __init__(self, name, preferred_courses: list[Course] = None, neutral_courses: list[Course] = None, unpreferred_courses: list[Course] = None):
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
        return f"Name: {self.name}. Teaching: {self.schedule}. Preferred: {self.preferred_courses}. Neutral: {self.neutral_courses}. Unpreferred: {self.unpreferred_courses}."
    
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
    def reset_schedule(self):
        """
        Resets the schedule of the student.
        """
        self.schedule = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        self.teaching_blocks = set()

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

    def find_best_block_for_course(self, course: Course, block_sections: dict[int, list[Section]]) -> int:
        """Finds the best block for a course based on the number of sections and teacher availability.
        
        Args:
            course (Course): The course to find the best block for.
        
        Returns:
            int: the best block
        """
        best_block = [-1, -1, math.inf] # [block, num_non_conflicting, num_conflicting]
        for block, sections in block_sections.items():
            if block in self.teaching_blocks:
                continue


            num_conflicting = 0
            num_non_conflicting = 0
            for section in sections:
                if section.course in course.conflicting_courses:
                    num_conflicting += 1

                    # doubly penalize the same class in the same block
                    if section.course == course:
                        num_conflicting += 1

                elif section.course in course.non_conflicting_courses:
                    num_non_conflicting += 1

            # algorithm to find the best block:
            # 1. minimize num_conflicting sections
            # 2. maximize num_non_conflicting sections
            # 3. if tied, find the block with the fewest sections overall
            # 4. if tied, randomly select a block
                        
            # step 1
            if num_conflicting < best_block[2]:
                best_block = [block, num_non_conflicting, num_conflicting]
            
            elif num_conflicting == best_block[2]:
                # step 2
                if num_non_conflicting > best_block[1]:
                    best_block = [block, num_non_conflicting, num_conflicting]

                elif num_non_conflicting == best_block[1]:
                    # step 3
                    if len(sections) < best_block[1] + best_block[2]:
                        best_block = [block, num_non_conflicting, num_conflicting]
            
                    elif len(sections) == best_block[1] + best_block[2]:
                        # step 4
                        if random.random() < 0.5:
                            best_block = [block, num_non_conflicting, num_conflicting]
        return best_block[0]
