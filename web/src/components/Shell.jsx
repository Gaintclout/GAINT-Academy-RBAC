import React, { useEffect, useState } from "react";
import { api } from "../api";
import Dashboard from "./Dashboard";
import RoleModule from "./RoleModule";
import ParentTracking from "./ParentTracking";
import LiveSafetyMap from "./LiveSafetyMap";
import Audit from "./Audit";
import StudentSafety from "./StudentSafety";
import StudentDashboard from "./StudentDashboard";
import StudentFinance from "./StudentFinance";
import StudentAcademicModule from "./StudentAcademicModule";
import InstitutionRoleDashboard from "./InstitutionRoleDashboard";
import AdaptiveRoleModule from "./AdaptiveRoleModule";
import InstitutionSetup from "./InstitutionSetup";
import AcademicStructure from "./AcademicStructure";
import AcademicAssignments from "./AcademicAssignments";
import TeacherAcademicWorkspace from "./TeacherAcademicWorkspace";
import StudentAssignedAcademics from "./StudentAssignedAcademics";
import AcademicWorkTeacher from "./AcademicWorkTeacher";
import AcademicWorkStudent from "./AcademicWorkStudent";
import TeacherSessions from "./TeacherSessions";
import StudentAttendanceTimetable from "./StudentAttendanceTimetable";
import GradeRules from "./GradeRules";
import StudentResults from "./StudentResults";
import { displayMenuLabel, getInstitutionUI } from "../institutionUI";

export default function Shell({ user, onLogout, onUserChange }) {
  const [menu, setMenu] = useState(["Dashboard"]);
  const [active, setActive] = useState("Dashboard");
  const [menuError, setMenuError] = useState("");
  const ui = getInstitutionUI(user);

  useEffect(() => {
    let cancelled = false;
    api.get("/api/v1/navigation")
      .then((response) => {
        if (cancelled) return;
        let items = response.data.items || ["Dashboard"];
        if (user.role === "Institution Admin") {
          if (!items.includes("Institution Setup")) items = [...items, "Institution Setup"];
          if (!items.includes("Academic Structure")) items = [...items, "Academic Structure"];
          if (!items.includes("Enrollment & Assignments")) items = [...items, "Enrollment & Assignments"];
          if (!items.includes("Grading Scheme")) items = [...items, "Grading Scheme"];
        }
        setMenu(items);
        setActive((current) => items.includes(current) ? current : "Dashboard");
        setMenuError("");
      })
      .catch((error) => {
        if (cancelled) return;
        setMenuError(error?.response?.data?.detail || "Unable to load navigation.");
      });
    return () => { cancelled = true; };
  }, [user.role]);

  let content;
  if (active === "Dashboard") {
    content = user.role === "Student" ? <StudentDashboard user={user} ui={ui} /> : <InstitutionRoleDashboard user={user} ui={ui} />;
  } else if (user.role === "Institution Admin" && active === "Institution Setup") {
    content = <InstitutionSetup user={user} onUpdated={(institution) => onUserChange?.({ ...user, institution })} />;
  } else if (user.role === "Institution Admin" && active === "Academic Structure") {
    content = <AcademicStructure ui={ui} />;
  } else if (user.role === "Institution Admin" && active === "Enrollment & Assignments") {
    content = <AcademicAssignments ui={ui} />;
  } else if (user.role === "Institution Admin" && active === "Grading Scheme") {
    content = <GradeRules ui={ui} />;
  } else if (user.role === "Student" && active === "Fees") {
    content = <StudentFinance ui={ui} />;
  } else if (user.role === "Student" && active === "Results") {
    content = <StudentResults ui={ui} />;
  } else if (user.role === "Student" && ["Timetable","Attendance"].includes(active)) {
    content = <StudentAttendanceTimetable title={active} ui={ui} />;
  } else if (user.role === "Teacher" && ["Timetable","Attendance"].includes(active)) {
    content = <TeacherSessions mode={active} ui={ui} />;
  } else if (user.role === "Student" && ["Homework","Assignments","Exams"].includes(active)) {
    content = <AcademicWorkStudent title={active} ui={ui} />;
  } else if (user.role === "Teacher" && ["Homework","Assignments","Exams"].includes(active)) {
    content = <AcademicWorkTeacher title={active} ui={ui} />;
  } else if (user.role === "Student" && ["Courses"].includes(active)) {
    content = <StudentAssignedAcademics title={active} ui={ui} />;
  } else if (user.role === "Teacher" && ["My Classes","My Students","Results"].includes(active)) {
    content = <TeacherAcademicWorkspace title={active} ui={ui} />;
  } else if (user.role === "Student" && ["My Profile","Transport","Library","Events","Grievance"].includes(active)) {
    content = <StudentAcademicModule title={active} ui={ui} />;
  } else if (user.role === "Parent / Guardian" && active === "Live Location") {
    content = <ParentTracking />;
  } else if (user.role === "Campus Admin" && active === "Live Safety Map") {
    content = <LiveSafetyMap />;
  } else if (user.role === "Student" && active === "My Safety") {
    content = <StudentSafety />;
  } else if ((user.role === "Auditor" && active === "Audit Trail") || (user.role === "Institution Admin" && active === "Audit")) {
    content = <Audit />;
  } else {
    content = <AdaptiveRoleModule title={active} user={user} ui={ui} />;
  }

  const initials = user.name
    ? user.name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase()
    : "GA";

  return (
    <div className={"shell institution-shell institution-" + ui.label.toLowerCase()}>
      <aside className="sidebar">
        <div className="side-brand">
          <div className="mini-mark">G</div>
          <div><b>GAINT</b><small>ACADEMY</small></div>
        </div>

        <div className="institution">
          <b>{ui.institutionName}</b>
          <small>{ui.subtitle}</small>
        </div>

        {menuError && <div className="sidebar-error">{menuError}</div>}

        <div className="menu">
          {menu.map((item) => (
            <button
              key={item}
              type="button"
              className={active === item ? "active" : ""}
              onClick={() => setActive(item)}
            >
              {displayMenuLabel(item, ui)}
            </button>
          ))}
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <input placeholder={ui.search} />
          <div className="topuser">
            <div className="avatar">{initials}</div>
            <div><b>{user.name}</b><small>{user.role} • {ui.label}</small></div>
            <button type="button" className="text-btn" onClick={onLogout}>Logout</button>
          </div>
        </header>
        <main className="content">{content}</main>
      </div>
    </div>
  );
}
