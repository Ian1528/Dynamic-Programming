import math
import random
import numpy as np
from params_old import *

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
        return f"{self.name} - {self.block}: {len(self.students)}"
    
    def add_student(self, student: "Student"):
        if student in self.students:
            print(student, self.students, self)
            raise Exception("Student is already in this section!")
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
    
    def reset_schedule(self):
        """
        Resets the schedule of the student.
        """
        self.schedule = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
    def add_course(self, course: Course, is_required=True):
        if is_required:
            self.required_courses.append(course)
        else:
            self.elective_courses.append(course)
            
    def add_section(self, section: Section):        
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
    def get_unassigned_courses(self) -> list[Course]:
        """
        Returns a list of all courses the student is enrolled in that are not assigned to a section yet.
        """
        return [course for course in self.get_all_courses() if course.name not in [section.name for section in self.schedule.values() if section is not None]]
    
    def get_available_sections_with_saturation(self, course: Course) -> dict[Section, int]:
        """
        Returns a list of all sections for a course that the student can be assigned to.
        """
        available_sections: list[Section] = []
        for section in course.sections:
            if self.schedule[section.block] is None:
                available_sections.append(section)

        blocks_to_sections = {section.block: section for section in available_sections}
        sections_saturations = {section: 0 for section in available_sections}
        available_sections_blocks: list[int] = [section.block for section in available_sections]
        for course in self.get_unassigned_courses():
            for section in course.get_unfilled_sections():
                if section.block in available_sections_blocks and not section.is_full():
                    corresponding_section = blocks_to_sections[section.block]
                    sections_saturations[corresponding_section] += 1
        
        # normalize the saturations 
        saturation_weights = np.array(list(sections_saturations.values()))
        saturation_weights = saturation_weights / np.sum(saturation_weights)

        if np.sum(saturation_weights) == 0:
            saturation_weights = np.ones(len(sections_saturations))/ len(sections_saturations)
        sections_saturations = {section: int(saturation_weights[i]*100) for i, section in enumerate(sections_saturations.keys())}
        
        return sections_saturations
    
    def reassign_block(self, block: int, blocks_to_avoid: list[int], layer_num: int) -> bool:
        """
        Attempts to reassigns whatever class is in the block. Returns True if successful, False otherwise. Recursively calls itself until it finds a block that is empty or determines that it's infeasible.
        """
        if len(blocks_to_avoid) >= len(self.schedule):
            return False
        
        old_section = self.schedule[block]
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
                    old_section.remove_student(self)
                    section.add_student(self)
                    return True



        # evaluate feasibility of switching to other sections
        
    def find_switch_section(self, section: Section, alpha: float = 1) -> Section:
        """
        Returns the other section of the course that the student can move this based on their frees.
        """
        all_sections = section.course.get_unfilled_sections()
        available_blocks = [section.block for section in all_sections if self.schedule[section.block] is None]
        available_blocks_to_sections = {section.block: section for section in all_sections if self.schedule[section.block] is None}
        if len(available_blocks) == 0:
            return None
        
        # pick the best section to switch into
        block_saturation = {block: 0 for block in available_blocks}
        block_population = {section.block: len(section.students) for section in all_sections if section.block in available_blocks}
        for course in self.get_unassigned_courses():
            for section in course.get_unfilled_sections():
                if section.block in block_saturation.keys() and not section.is_full():
                    block_saturation[section.block] += 1

        saturation_weights = np.array(list(block_saturation.values()))
        population_weights = np.array(list(block_population.values()))
        
        if np.sum(saturation_weights) == 0:
            saturation_weights = np.ones(len(saturation_weights))/ len(saturation_weights)
        saturation_weights = saturation_weights / np.sum(saturation_weights)
        population_weights = population_weights / np.sum(population_weights)

        combined_weights = (1 - alpha) * saturation_weights + alpha * population_weights

        best_block = [-1, math.inf, math.inf, math.inf] # [block, combined, population, saturation]
        for i, (block, section) in enumerate(available_blocks_to_sections.items()):
            if combined_weights[i] < best_block[1]:
                best_block = [block, combined_weights[i], population_weights[i], saturation_weights[i]]
            
            elif combined_weights[i] == best_block[1]:
                # step 2
                if population_weights[i] < best_block[2]:
                    best_block = [block, combined_weights[i], population_weights[i], saturation_weights[i]]

                elif population_weights[i] == best_block[2]:
                    # step 3
                    if saturation_weights[i] < best_block[3]:
                        best_block = [block, combined_weights[i], population_weights[i], saturation_weights[i]]
        return available_blocks_to_sections[best_block[0]]

    def get_optimal_section(self, course: Course, alpha: float = 1) -> Section:
        """
        Given a student and a course, returns the optimal section for that student.
        Optimal section based on the following: current number of students

        Args:
            course (Course): The course to assign the student to.
            alpha (float): The weight for the population of the section. 0 means only consider saturation, 1 means only consider population.

        Returns:
            Section: The specific section that is optimal for the student.
        """

        available_sections = course.get_unfilled_sections()
        available_blocks_to_sections_for_course = {section.block: section for section in available_sections}

        if len(available_sections) == 0:
            raise Exception("No available sections remaining for this course! Need more teachers.")
        
        available_blocks_to_sections = {section.block: section for section in available_sections if self.schedule[section.block] is None}
        courses_remaining = self.get_unassigned_courses()
        
        if len(available_blocks_to_sections) == 0:
            print("No available sections, need to attempt to rearrange schedule")
            for block, other_course_section in self.schedule.items():
                if other_course_section is not None and block in available_blocks_to_sections_for_course.keys():
                    switched_section = self.find_switch_section(other_course_section)
                    if switched_section is not None:
                        print("Can switch section")
                        # remove from the old section
                        other_course_section.remove_student(self)
                        switched_section.add_student(self)

                        return available_blocks_to_sections_for_course[block]

            raise Exception("No available blocks remaining for this course! Need more teachers.")
        block_saturation = {block: 0 for block in available_blocks_to_sections.keys()}
        block_population = {section.block: len(section.students) for section in available_sections if section.block in available_blocks_to_sections.keys()}
        for course in courses_remaining:
            for section in course.get_unfilled_sections():
                if section.block in block_saturation.keys() and not section.is_full():
                    block_saturation[section.block] += 1
        
        saturation_weights = np.array(list(block_saturation.values()))
        population_weights = np.array(list(block_population.values()))
        saturation_weights = saturation_weights / np.sum(saturation_weights)
        population_weights = population_weights / np.sum(population_weights)

        combined_weights = (1 - alpha) * saturation_weights + alpha * population_weights

        best_block = [-1, math.inf, math.inf, math.inf] # [block, combined, population, saturation]
        for i, (block, section) in enumerate(available_blocks_to_sections.items()):
            if combined_weights[i] < best_block[1]:
                best_block = [block, combined_weights[i], population_weights[i], saturation_weights[i]]
            
            elif combined_weights[i] == best_block[1]:
                # step 2
                if population_weights[i] < best_block[2]:
                    best_block = [block, combined_weights[i], population_weights[i], saturation_weights[i]]

                elif population_weights[i] == best_block[2]:
                    # step 3
                    if saturation_weights[i] < best_block[3]:
                        best_block = [block, combined_weights[i], population_weights[i], saturation_weights[i]]
        return available_blocks_to_sections[best_block[0]]

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
        best_block = [-1, -1, math.inf] # [block, num_same_subject, num_diff_subject]
        for block, sections in block_sections.items():
            if block in self.teaching_blocks:
                continue

            # compute overlap with sections of the same subject, and non overlapping classes
            num_same_subject = 0 
            num_diff_subject = 0
            for section in sections:
                if section.name.startswith(course.name[0:3]):
                    # check if the teacher is already teaching a section in this block
                    num_same_subject += 1
                else:
                    num_diff_subject += 1

            # algorithm to find the best block:
            # 1. find the block with the most sections of the same subject (b/c students aren't likely to take both)
            # 2. if tied, find the block with the fewest sections of a different subject
            # 3. if tied, find the block with the fewest sections overall
            # 4. if tied, randomly select a block
            
            # step 1
            if num_same_subject > best_block[1]:
                best_block = [block, num_same_subject, num_diff_subject]
            
            elif num_same_subject == best_block[1]:
                # step 2
                if num_diff_subject < best_block[2]:
                    best_block = [block, num_same_subject, num_diff_subject]

                elif num_diff_subject == best_block[2]:
                    # step 3
                    if len(sections) < best_block[1] + best_block[2]:
                        best_block = [block, num_same_subject, num_diff_subject]
            
                    elif len(sections) == best_block[1] + best_block[2]:
                        # step 4
                        if random.random() < 0.5:
                            best_block = [block, num_same_subject, num_diff_subject]
        return best_block[0]
