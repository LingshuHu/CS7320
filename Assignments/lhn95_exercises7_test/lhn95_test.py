import pytest
import System
import Student
import RestoreData
from datetime import datetime as dt

student1 = 'akend3'
student1_pwd =  '123454321'
student2 = 'hdjsr7'
student2_pwd = 'pass1234'
student3 = 'yted91'
student3_pwd = 'imoutofpasswordnames'
TA = 'cmhbf5' 
TA_pwd = 'bestTA'
prof1 = 'goggins'
prof1_pwd = 'augurrox'
prof2 = 'saab'
prof2_pwd = 'boomr345'
sub_date = '10/9/20'

@pytest.fixture
def grading_system():
    gradingSystem = System.System()
    gradingSystem.load_data()
    return gradingSystem


# 1. login - System.py pass
def test_login(grading_system):
    users = grading_system.users
    grading_system.login(student1,student1_pwd)
    grading_system.__init__()

    if grading_system.usr.name != student1:
        assert False
    if grading_system.usr.courses != users[student1]['courses']:
        assert False
    if not isinstance(grading_system.usr, Student.Student):
        assert False


# 2. check_password - System.py pass
def test_check_password(grading_system):
    test = grading_system.check_password(student1,student1_pwd)
    test2 = grading_system.check_password(student1,'123454321')
    test3 = grading_system.check_password(student1,'1234543')
    test4 = grading_system.check_password(student1,'sdfkoen')
    if test == test3 or test2 == test3 or test == test4 or test2 == test4:
        assert False
    if test != test2:
        assert False


# 3. change_grade - Staff.py fail
def test_change_grade(grading_system):
    grading_system.login(TA, TA_pwd)
    grading_system.usr.change_grade('yted91', 'software_engineering', 'assignment2', 99)
    grading_system.usr.update_user_db
    users = grading_system.users
    if users['yted91']['courses']['software_engineering']['assignment2']['grade'] != 99:
        assert False


# 4. create_assignment Staff.py pass
def test_create_assignment(grading_system):
    grading_system.login(prof2, prof2_pwd)
    grading_system.usr.create_assignment('assignment_extra', '10/13/20', 'software_engineering')
    courses = grading_system.courses
    if 'assignment_extra' not in courses['software_engineering']['assignments']:
        assert False
    if '10/13/20' != courses['software_engineering']['assignments']['assignment_extra']['due_date']:
        assert False


# 5. add_student - Professor.py
def test_add_student(grading_system):
    grading_system.login(prof2, prof2_pwd)
    try:
        grading_system.usr.add_student('lhn95', 'comp_sci')
    except TypeError:
        users = grading_system.users
        if 'lhn95' not in users:
            assert False
        if 'comp_sci' not in users['lhn95']['courses']:
            assert False


# 6. drop_student Professor.py
def test_drop_student(grading_system):
    grading_system.login(prof2, prof2_pwd)
    grading_system.usr.drop_student('yted91', 'cloud_computing')
    users = grading_system.users
    if 'cloud_computing' in users['yted91']['courses']:
        assert False


# 7. submit_assignment - Student.py 
# ### due date is wrong.
def test_submit_assignment(grading_system):
    grading_system.login(student2, student2_pwd)
    grading_system.usr.submit_assignment('databases', 'assignment1', 'redid the work', '10/09/20')
    users = grading_system.users
    if 'assignment1' not in users[student2]['courses']['databases']:
        assert False
    if 'redid the work' != users[student2]['courses']['databases']['assignment1']['submission']:
        assert False
    if '10/09/20' != users[student2]['courses']['databases']['assignment1']['submission_date']:
        assert False
    ## get course assignment due date
    courses = grading_system.courses
    duedate = courses['databases']['assignments']['assignment1']['due_date']
    ## compare if it is really ontime
    duedate = dt.strptime(duedate, '%m/%d/%y')
    subdate = dt.strptime('10/09/20', '%m/%d/%y')
    ontime = subdate <= duedate
    if ontime != users[student2]['courses']['databases']['assignment1']['ontime']:
        assert False


# 8. check_ontime - Student.py
def test_check_ontime(grading_system):
    grading_system.login(student2, student2_pwd)
    grading_system.usr.submit_assignment('databases', 'assignment1', 'redid the work', '10/09/20')
    ## get course assignment due date
    courses = grading_system.courses
    duedate = courses['databases']['assignments']['assignment1']['due_date']
    ## check ontime
    check = grading_system.usr.check_ontime('10/09/20', duedate) 
    ## compare if it is really ontime
    duedate = dt.strptime(duedate, '%m/%d/%y')
    subdate = dt.strptime('10/09/20', '%m/%d/%y')
    ontime = subdate <= duedate

    if check != ontime:
        assert False

    
# 9. check_grades - Student.py
def test_check_grades(grading_system):
    grading_system.login(student2, student2_pwd)
    grades = grading_system.usr.check_grades('databases')
    assignments = grading_system.users[student2]['courses']['databases']
    true_grades = []
    for key in assignments:
        true_grades.append(assignments[key]['grade'])
    if len(grades) != len(true_grades):
        assert False
    for i in range(len(grades)):
        if grades[i][1] != true_grades[i]:
            assert False


# 10. view_assignments - Student.py
def test_view_assignments(grading_system):
    grading_system.login(student2, student2_pwd)
    assignments = grading_system.usr.view_assignments('databases')
    true_assignments = []
    assign = grading_system.courses['databases']['assignments']
    for key in assign:
        true_assignments.append([key, assign[key]['due_date']])
    if len(assignments) != len(true_assignments):
        assert False
    for i in range(len(assignments)):
        if assignments[i] != true_assignments[i]:
            assert False


# 11. Test if professors can create assignments for a class they are not teaching
def test_create_assignment_wrong_class(grading_system):
    grading_system.login(prof2, prof2_pwd)
    courses = grading_system.courses
    grading_system.usr.create_assignment('assignment_extra', '10/13/20', 'software_engineering')
    if prof2 != courses['software_engineering']['professor'] and 'assignment_extra' in courses['software_engineering']['assignments']:
        assert False


# 12. Test if TAs can change students' grade from a class they are not shadowing
def test_change_grade_wrong_class(grading_system):
    grading_system.login(TA, TA_pwd)
    ## get original grade
    grade_old = grading_system.users[student2]['courses']['databases']['assignment2']['grade']
    changed_grade = grade_old - 20
    grading_system.usr.change_grade(student2, 'databases', 'assignment2', changed_grade)
    grading_system.usr.update_user_db
    grade_new = grading_system.users[student2]['courses']['databases']['assignment2']['grade']
    if grade_new != grade_old:
        assert False


# 13. Test if professors can drop students from a class they are not teaching
def test_drop_student_wrong_class(grading_system):
    grading_system.login(prof2, prof2_pwd)
    grading_system.usr.drop_student('yted91', 'software_engineering')
    users = grading_system.users
    if 'software_engineering' not in users['yted91']['courses']:
        assert False


# 14. Test if TAs can check students' grade from a class they are not shadowing
def test_check_grades_wrong_class(grading_system):
    grading_system.login(TA, TA_pwd)
    grades = grading_system.usr.check_grades(student2, 'databases')
    assignments = grading_system.users[student2]['courses']['databases']
    true_grades = []
    for key in assignments:
        true_grades.append([key, assignments[key]['grade']])
    if grades == true_grades:
        assert False


# 15. Test if there limitations for password
def test_password_format(grading_system):
    ## password should have both letters and numbers and more than 5 length
    pwds = []
    for user in grading_system.users:
        pwds.append(grading_system.users[user]['password'])
    if any(len(p) < 5 for p in pwds): 
        assert False
    if any(p.isdigit() for p in pwds):
        assert False
    if any(p.isalpha() for p in pwds):
        assert False
