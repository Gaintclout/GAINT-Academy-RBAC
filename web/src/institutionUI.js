export const INSTITUTION_UI = {
  SCHOOL: {
    label: "School",
    institutionName: "GAINT Demo School",
    subtitle: "Academic Year 2026-27",
    search: "Search classes, homework, results...",
    menuMap: {
      Dashboard: "Dashboard",
      "My Profile": "My Profile",
      Timetable: "Timetable",
      Attendance: "Attendance",
      Courses: "My Classes",
      Homework: "Homework",
      Assignments: "Assignments",
      Exams: "Exams",
      Results: "Results",
      Fees: "My Fees",
      Transport: "My Bus",
      Library: "Library",
      Events: "Activities",
      Grievance: "Grievance",
      "My Safety": "My Safety",
      Staff: "Teachers & Staff", Admissions: "Admissions", Academics: "Classes & Subjects", "Exams & Results": "Exams & Report Cards", Communication: "School Communication", "Learning / LMS": "Learning Resources", "Fees & Payments": "School Fees", Hostel: "Boarding / Hostel", "Inventory & Assets": "School Assets", Health: "Student Health", "Users & Roles": "Users & Roles", "My Classes": "My Classes", "My Students": "My Students", "Teacher Notes": "Teacher Notes", Leave: "Leave", "My Children": "My Children", "Live Location": "School Bus / Live Location", Messages: "Messages", "Leave Request": "Leave Request", Payments: "Payments", Receipts: "Receipts", Concessions: "Concessions", Refunds: "Refunds", Reconciliation: "Reconciliation", "Finance Reports": "Finance Reports", Documents: "Staff Documents", Recruitment: "Recruitment", Performance: "Staff Performance", "HR Reports": "HR Reports", "Campus Attendance": "School Attendance", "Live Safety Map": "School Safety Map", Visitors: "Visitors", Inventory: "Inventory", Assets: "Assets", Reports: "Reports", "Audit Trail": "Audit Trail", Compliance: "Compliance", "Exception Reports": "Exception Reports", Evidence: "Evidence", "Export Reports": "Export Reports"
    },
    dashboard: {
      greeting: "Good Morning",
      subtitle: "Here is your school day at a glance.",
      cards: [
        ["Today's Classes", "6", "2 before lunch"],
        ["Homework", "3 Pending", "1 due tomorrow"],
        ["My Bus", "12 min", "Route A1"],
        ["Attendance", "92%", "This term"]
      ]
    }
  },
  COLLEGE: {
    label: "College",
    institutionName: "GAINT Demo College",
    subtitle: "Semester IV • 2026-27",
    search: "Search courses, assignments, placements...",
    menuMap: {
      Dashboard: "Dashboard",
      "My Profile": "My Profile",
      Timetable: "Semester",
      Attendance: "Attendance",
      Courses: "My Courses",
      Homework: "Coursework",
      Assignments: "Assignments",
      Exams: "Exams",
      Results: "Results",
      Fees: "Fees",
      Transport: "Campus Transport",
      Library: "Library",
      Events: "Clubs & Societies",
      Grievance: "Student Support",
      "My Safety": "Safety & Emergency",
      Staff: "Faculty & Staff", Admissions: "Admissions", Academics: "Departments & Programs", "Exams & Results": "Examinations & Results", Communication: "Campus Communication", "Learning / LMS": "Digital Learning", "Fees & Payments": "Semester Fees & Payments", Hostel: "Hostel", "Inventory & Assets": "Campus Assets", Health: "Student Wellness", "Users & Roles": "Users & Roles", "My Classes": "My Courses", "My Students": "Advisees / Students", "Teacher Notes": "Faculty Notes", Leave: "Leave", "My Children": "Student Overview", "Live Location": "Campus Transport", Messages: "Messages", "Leave Request": "Leave Request", Payments: "Payments", Receipts: "Receipts", Concessions: "Scholarships / Concessions", Refunds: "Refunds", Reconciliation: "Reconciliation", "Finance Reports": "Finance Reports", Documents: "Faculty & Staff Documents", Recruitment: "Recruitment", Performance: "Performance", "HR Reports": "HR Reports", "Campus Attendance": "Campus Attendance", "Live Safety Map": "Campus Safety Map", Visitors: "Visitors", Inventory: "Inventory", Assets: "Campus Assets", Reports: "Reports", "Audit Trail": "Audit Trail", Compliance: "Compliance", "Exception Reports": "Exception Reports", Evidence: "Evidence", "Export Reports": "Export Reports"
    },
    dashboard: {
      greeting: "Welcome back",
      subtitle: "Track your semester, credits and career readiness.",
      cards: [
        ["CGPA", "8.4 / 10", "Strong standing"],
        ["Attendance", "87%", "Across courses"],
        ["Credits Earned", "72 / 120", "Semester IV"],
        ["Assignments", "3 Pending", "Next due Sep 28"]
      ]
    }
  },
  UNIVERSITY: {
    label: "University",
    institutionName: "GAINT Demo University",
    subtitle: "School of Engineering • 2026-27",
    search: "Search programs, courses, research...",
    menuMap: {
      Dashboard: "Dashboard",
      "My Profile": "My Program",
      Timetable: "Courses",
      Attendance: "Attendance",
      Courses: "Credits",
      Homework: "Coursework",
      Assignments: "Assessments",
      Exams: "Examinations",
      Results: "Academic Records",
      Fees: "Student Finance",
      Transport: "Campus Services",
      Library: "Library",
      Events: "Research & Events",
      Grievance: "Student Support",
      "My Safety": "Campus Safety",
      Staff: "Faculty & Staff", Admissions: "Admissions & Enrollment", Academics: "Schools, Programs & Curriculum", "Exams & Results": "Assessment & Academic Records", Communication: "University Communication", "Learning / LMS": "Digital Learning", "Fees & Payments": "Student Finance", Hostel: "Residence / Hostel", "Inventory & Assets": "University Assets", Health: "Health & Wellness", "Users & Roles": "Identity & Roles", "My Classes": "My Courses", "My Students": "Advisees", "Teacher Notes": "Faculty Notes", Leave: "Leave", "My Children": "Student Overview", "Live Location": "Campus Services / Location", Messages: "Messages", "Leave Request": "Leave Request", Payments: "Student Payments", Receipts: "Receipts & Statements", Concessions: "Scholarships & Financial Aid", Refunds: "Refunds", Reconciliation: "Finance Reconciliation", "Finance Reports": "Financial Analytics", Documents: "Faculty & Staff Records", Recruitment: "Talent Acquisition", Performance: "Faculty & Staff Performance", "HR Reports": "Workforce Analytics", "Campus Attendance": "Campus Presence", "Live Safety Map": "Campus Safety Operations", Visitors: "Visitors", Inventory: "Inventory", Assets: "Facilities & Assets", Reports: "Institutional Reports", "Audit Trail": "Audit Trail", Compliance: "Governance & Compliance", "Exception Reports": "Risk & Exceptions", Evidence: "Audit Evidence", "Export Reports": "Audit Reports"
    },
    dashboard: {
      greeting: "Welcome back",
      subtitle: "Your academic, research and campus overview.",
      cards: [
        ["CGPA", "8.6 / 10", "Cumulative"],
        ["Credits", "96 / 160", "Program progress"],
        ["Attendance", "91%", "Current semester"],
        ["Research", "2 Publications", "1 active project"]
      ]
    }
  }
};

export function resolveInstitutionType(user) {
  const configured = String(user?.institution?.institution_type || import.meta.env.VITE_INSTITUTION_TYPE || "UNIVERSITY").toUpperCase();
  return INSTITUTION_UI[configured] ? configured : "UNIVERSITY";
}

export function getInstitutionUI(user) {
  const base = INSTITUTION_UI[resolveInstitutionType(user)];
  return user?.institution?.name ? { ...base, institutionName: user.institution.name } : base;
}

export function displayMenuLabel(item, ui = getInstitutionUI()) {
  return ui.menuMap[item] || item;
}
