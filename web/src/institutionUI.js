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
      "My Safety": "My Safety"
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
      "My Safety": "Safety & Emergency"
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
      "My Safety": "Campus Safety"
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

export function resolveInstitutionType() {
  const configured = String(import.meta.env.VITE_INSTITUTION_TYPE || "UNIVERSITY").toUpperCase();
  return INSTITUTION_UI[configured] ? configured : "UNIVERSITY";
}

export function getInstitutionUI() {
  return INSTITUTION_UI[resolveInstitutionType()];
}

export function displayMenuLabel(item, ui = getInstitutionUI()) {
  return ui.menuMap[item] || item;
}
