import React from "react";
import { api } from "../api";

const MODULES = {
  School: {
    "My Profile": { title:"My Profile", subtitle:"Student identity and school information", stats:[["Student ID","STU-1001"],["Class","10-A"],["House","Blue"],["Academic Year","2026-27"]], rows:[["Class Teacher","Ms. Ananya Rao"],["Parent Contact","Linked"],["Blood Group","O+"],["Status","Active"]] },
    Timetable: { title:"My Timetable", subtitle:"Today's school periods", stats:[["Periods Today","7"],["Next Class","Mathematics"],["Lunch","12:30 PM"],["School Ends","3:30 PM"]], rows:[["09:00","Mathematics","Room 101","Ms. Rao"],["10:00","Science","Lab 2","Mr. Kumar"],["11:00","English","Room 102","Ms. Devi"],["01:30","Social Studies","Room 103","Mr. Ali"]] },
    Attendance: { title:"My Attendance", subtitle:"Daily attendance for this term", stats:[["Attendance","92%"],["Present","83"],["Absent","7"],["Late","2"]], rows:[["23 Sep 2026","Present","Full Day","Recorded"],["22 Sep 2026","Present","Full Day","Recorded"],["21 Sep 2026","Absent","Medical","Approved"]] },
    Courses: { title:"My Classes", subtitle:"Subjects and teachers", stats:[["Subjects","7"],["Core","5"],["Activities","2"],["Class","10-A"]], rows:[["Mathematics","MAT-10","Ms. Rao","Active"],["Science","SCI-10","Mr. Kumar","Active"],["English","ENG-10","Ms. Devi","Active"],["Computer Science","CS-10","Lab 1","Active"]] },
    Homework: { title:"Homework", subtitle:"Homework assigned by your teachers", stats:[["Pending","3"],["Submitted","8"],["Due Tomorrow","1"],["This Week","5"]], rows:[["Algebra Chapter 4","MAT-104","Due 26 Sep","Pending"],["Science Worksheet","SCI-206","Submitted","Completed"],["English Essay","ENG-112","Due 28 Sep","Pending"]] },
    Assignments: { title:"Assignments", subtitle:"Projects and class assignments", stats:[["Open","2"],["Submitted","6"],["Graded","5"],["Average","89%"]], rows:[["Science Model","SCI-A12","30 Sep","In Progress"],["Book Review","ENG-A08","27 Sep","Submitted"],["Math Activity","MAT-A14","02 Oct","Pending"]] },
    Exams: { title:"Exams", subtitle:"School examination schedule", stats:[["Upcoming","2"],["Completed","4"],["Next Exam","Mathematics"],["Starts In","5 Days"]], rows:[["Mathematics","EX-MAT","30 Sep 09:30","Upcoming"],["Science","EX-SCI","02 Oct 09:30","Upcoming"],["English","EX-ENG","18 Sep","Completed"]] },
    Results: { title:"Results", subtitle:"Marks and grades", stats:[["Average","90%"],["Grade","A+"],["Rank","8"],["Subjects","7"]], rows:[["Mathematics","92/100","A+","Published"],["Science","88/100","A","Published"],["English","91/100","A+","Published"]] },
    Transport: { title:"My Bus", subtitle:"School transport and pickup information", stats:[["Route","A1"],["Bus","GAINT BUS 12"],["Pickup","08:00 AM"],["ETA","12 min"]], rows:[["Home Pickup","STOP-01","08:00","Active"],["School","STOP-12","08:45","Destination"]] },
    Library: { title:"Library", subtitle:"Books borrowed and due dates", stats:[["Borrowed","2"],["Available Limit","3"],["Due Soon","1"],["Fine","₹0"]], rows:[["Wings of Fire","BK-109","28 Sep","Borrowed"],["Young Scientist","BK-220","04 Oct","Borrowed"]] },
    Events: { title:"Activities", subtitle:"School activities and events", stats:[["Upcoming","4"],["Clubs","2"],["Sports","1"],["Registered","3"]], rows:[["Science Fair","EV-21","28 Sep","Registered"],["Sports Day","EV-24","05 Oct","Upcoming"],["Art Club","CL-08","Friday","Active"]] },
    Grievance: { title:"Grievance", subtitle:"Raise and track student support requests", stats:[["Open","0"],["Resolved","2"],["Response SLA","48 hrs"],["Channel","Student Support"]], rows:[["Library Card Issue","GR-102","Resolved","Closed"]] }
  },
  College: {
    "My Profile": { title:"Student Profile", subtitle:"Program, semester and academic identity", stats:[["Student ID","CSE-23041"],["Program","B.Tech CSE"],["Semester","IV"],["Batch","2025-29"]], rows:[["Department","Computer Science","UG","Active"],["Advisor","Dr. Ananya Rao","Faculty","Assigned"],["Section","CSE-A","Semester IV","Active"]] },
    Timetable: { title:"Semester Schedule", subtitle:"Lectures, labs and academic sessions", stats:[["Courses","6"],["Labs","2"],["Credits","24"],["Today","5 Sessions"]], rows:[["09:00","Data Structures","CSE-204","LH-3"],["10:00","DBMS","CSE-206","LH-5"],["11:30","DS Lab","CSE-L204","Lab 2"],["02:00","Discrete Mathematics","MAT-202","LH-2"]] },
    Attendance: { title:"Attendance", subtitle:"Course-wise semester attendance", stats:[["Overall","87%"],["Best","DBMS 94%"],["Below 80%","1 Course"],["Sessions","126"]], rows:[["Data Structures","CSE-204","86%","Eligible"],["DBMS","CSE-206","94%","Eligible"],["Discrete Mathematics","MAT-202","78%","Attention"]] },
    Courses: { title:"My Courses", subtitle:"Registered semester courses and credits", stats:[["Registered","6"],["Credits","24"],["Core","5"],["Elective","1"]], rows:[["Data Structures","CSE-204","4 Credits","Core"],["DBMS","CSE-206","4 Credits","Core"],["Cloud Fundamentals","CSE-EL2","3 Credits","Elective"]] },
    Homework: { title:"Coursework", subtitle:"Faculty coursework and learning tasks", stats:[["Pending","3"],["Completed","11"],["Due This Week","2"],["Courses","6"]], rows:[["SQL Query Set","CSE-206","28 Sep","Pending"],["Trees & Graphs","CSE-204","30 Sep","Pending"],["Probability Sheet","MAT-202","Submitted","Completed"]] },
    Assignments: { title:"Assignments & Projects", subtitle:"Academic submissions and project reviews", stats:[["Open","3"],["Submitted","8"],["Graded","6"],["Project","1 Active"]], rows:[["Mini Project Proposal","CSE-P01","02 Oct","In Progress"],["DBMS Case Study","CSE-206-A2","29 Sep","Submitted"],["DS Coding Assignment","CSE-204-A3","28 Sep","Pending"]] },
    Exams: { title:"Examinations", subtitle:"Internal and semester examination schedule", stats:[["Internals","2"],["Labs","1"],["Semester Exam","Upcoming"],["Hall Ticket","Available"]], rows:[["DBMS Internal II","CSE-206","02 Oct","Upcoming"],["Data Structures Internal II","CSE-204","04 Oct","Upcoming"],["DS Lab Practical","CSE-L204","08 Oct","Scheduled"]] },
    Results: { title:"Academic Results", subtitle:"Semester grades and academic performance", stats:[["SGPA","8.6"],["CGPA","8.4"],["Credits Earned","72"],["Backlogs","0"]], rows:[["Semester III","SGPA 8.6","24 Credits","Completed"],["Semester II","SGPA 8.3","24 Credits","Completed"],["Semester I","SGPA 8.2","24 Credits","Completed"]] },
    Transport: { title:"Campus Transport", subtitle:"College shuttle and route information", stats:[["Route","C-04"],["Shuttle","BUS 08"],["Pickup","07:45 AM"],["Pass","Active"]], rows:[["Malkajgiri","STOP-C04","07:45","Pickup"],["Main Campus","CAMPUS","08:35","Destination"]] },
    Library: { title:"College Library", subtitle:"Books, journals and borrowing status", stats:[["Borrowed","3"],["Limit","6"],["Journals","Online"],["Fine","₹0"]], rows:[["Database System Concepts","ISBN-DB01","04 Oct","Borrowed"],["Algorithms","ISBN-AL22","08 Oct","Borrowed"],["Computer Networks","ISBN-CN18","12 Oct","Borrowed"]] },
    Events: { title:"Clubs & Societies", subtitle:"Technical, cultural and campus activities", stats:[["Clubs","3"],["Events","5"],["Hackathons","1"],["Registered","2"]], rows:[["Coding Club","CL-CODE","Friday","Active"],["Tech Fest","EV-TF26","12 Oct","Registered"],["Hackathon","EV-HK09","18 Oct","Upcoming"]] },
    Grievance: { title:"Student Support", subtitle:"Academic and campus support requests", stats:[["Open","1"],["Resolved","3"],["Advisor","Assigned"],["SLA","48 hrs"]], rows:[["Lab Access Request","SUP-204","IT Services","In Review"],["ID Card Replacement","SUP-181","Admin","Resolved"]] }
  },
  University: {
    "My Profile": { title:"My Program", subtitle:"University program and academic standing", stats:[["Scholar ID","UNI-CSE-441"],["Program","B.Tech CSE"],["School","Engineering"],["Year","III"]], rows:[["Specialization","AI & Data Science","Major","Active"],["Faculty Advisor","Dr. Ananya Rao","CSE","Assigned"],["Academic Standing","Good","CGPA 8.6","Active"]] },
    Timetable: { title:"Courses", subtitle:"University course registration and schedule", stats:[["Registered","5"],["Credits","22"],["Core","3"],["Electives","2"]], rows:[["Machine Learning","CSE-601","4 Credits","Mon/Wed"],["Distributed Systems","CSE-603","4 Credits","Tue/Thu"],["Research Methods","RES-501","3 Credits","Friday"]] },
    Attendance: { title:"Attendance", subtitle:"Course participation and eligibility", stats:[["Overall","91%"],["Courses","5"],["Below Threshold","0"],["Sessions","108"]], rows:[["Machine Learning","CSE-601","92%","Eligible"],["Distributed Systems","CSE-603","89%","Eligible"],["Research Methods","RES-501","95%","Eligible"]] },
    Courses: { title:"Credits & Curriculum", subtitle:"Program credits and degree progress", stats:[["Earned","96"],["Required","160"],["Current","22"],["Progress","60%"]], rows:[["Core Credits","CORE","68","Completed"],["Electives","ELEC","18","In Progress"],["Research","RES","10","In Progress"]] },
    Homework: { title:"Coursework", subtitle:"University coursework and learning activities", stats:[["Open","4"],["Completed","14"],["Research Tasks","2"],["Due This Week","3"]], rows:[["ML Model Evaluation","CSE-601","29 Sep","Pending"],["Distributed Cache Review","CSE-603","01 Oct","Pending"],["Literature Survey","RES-501","04 Oct","In Progress"]] },
    Assignments: { title:"Assessments & Projects", subtitle:"Course assessments, projects and research submissions", stats:[["Assessments","4"],["Projects","2"],["Submitted","9"],["Research","1 Active"]], rows:[["ML Capstone","CSE-601-P","15 Oct","In Progress"],["Distributed Systems Project","CSE-603-P","20 Oct","In Progress"],["Research Proposal","RES-501-A","05 Oct","Submitted"]] },
    Exams: { title:"Examinations", subtitle:"University examination and evaluation schedule", stats:[["Upcoming","3"],["Hall Ticket","Available"],["Internal","Completed"],["End Semester","Nov 2026"]], rows:[["Machine Learning","CSE-601","12 Nov","Scheduled"],["Distributed Systems","CSE-603","15 Nov","Scheduled"],["Research Methods","RES-501","18 Nov","Scheduled"]] },
    Results: { title:"Academic Records", subtitle:"Transcript, grades and cumulative performance", stats:[["CGPA","8.6"],["Credits","96"],["Completed Terms","5"],["Standing","Good"]], rows:[["Semester V","SGPA 8.8","22 Credits","Completed"],["Semester IV","SGPA 8.5","24 Credits","Completed"],["Semester III","SGPA 8.6","24 Credits","Completed"]] },
    Transport: { title:"Campus Services", subtitle:"Transport and student campus services", stats:[["Shuttle","Route U2"],["Hostel","H4"],["ID Access","Active"],["Service Requests","0"]], rows:[["Campus Shuttle","U2","07:30-20:00","Active"],["Hostel Access","H4","24x7","Active"],["Sports Complex","SC-1","06:00-21:00","Available"]] },
    Library: { title:"University Library", subtitle:"Books, journals, repositories and research resources", stats:[["Borrowed","4"],["E-Journals","12,000+"],["Databases","18"],["Fine","₹0"]], rows:[["Deep Learning","BK-DL90","10 Oct","Borrowed"],["IEEE Digital Library","DB-IEEE","Online","Active"],["Research Repository","UNI-REP","Online","Active"]] },
    Events: { title:"Research & Events", subtitle:"Research seminars, conferences and university activities", stats:[["Seminars","3"],["Conferences","1"],["Research Meets","2"],["Registered","3"]], rows:[["AI Research Seminar","RES-E21","03 Oct","Registered"],["Innovation Summit","UNI-E31","15 Oct","Upcoming"],["Research Colloquium","RES-E28","22 Oct","Upcoming"]] },
    Grievance: { title:"Student Support", subtitle:"Academic, administrative and campus support", stats:[["Open","1"],["Resolved","5"],["Escalations","0"],["SLA","72 hrs"]], rows:[["Transcript Request","SUP-U92","Registrar","In Review"],["Research Lab Access","SUP-U84","School Office","Resolved"]] }
  }
};

export default function StudentAcademicModule({ title, ui }) {
  const data = MODULES[ui.label]?.[title];
  if (!data) return null;

  async function raiseSupport() {
    try {
      await api.post("/api/v1/module-actions/create_grievance", { page: "Grievance", details: "Student support request from adaptive UI." });
      window.alert("Support request submitted.");
    } catch (e) {
      window.alert(e?.response?.data?.detail || "Unable to submit request.");
    }
  }

  return (
    <div className={"student-module student-module-" + ui.label.toLowerCase()}>
      <div className="page-title">
        <div><span className="eyebrow">{ui.label} Student</span><h1>{data.title}</h1><p>{data.subtitle}</p></div>
        {title === "Grievance" && <button className="primary" type="button" onClick={raiseSupport}>Raise Request</button>}
      </div>
      <div className="module-kpis">
        {data.stats.map(([label,value]) => <article key={label}><small>{label}</small><strong>{value}</strong></article>)}
      </div>
      <section className="panel">
        <div className="panel-title"><b>{data.title} Details</b><span>Current</span></div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>Item</th><th>Reference</th><th>Details</th><th>Status / Info</th></tr></thead>
            <tbody>{data.rows.map((row) => <tr key={row.join("-")}><td><b>{row[0]}</b></td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
