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
import { displayMenuLabel, getInstitutionUI } from "../institutionUI";

export default function Shell({ user, onLogout }) {
  const [menu, setMenu] = useState(["Dashboard"]);
  const [active, setActive] = useState("Dashboard");
  const [menuError, setMenuError] = useState("");
  const ui = getInstitutionUI();

  useEffect(() => {
    let cancelled = false;
    api.get("/api/v1/navigation")
      .then((response) => {
        if (cancelled) return;
        const items = response.data.items || ["Dashboard"];
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
  } else if (user.role === "Student" && active === "Fees") {
    content = <StudentFinance ui={ui} />;
  } else if (user.role === "Student" && ["My Profile","Timetable","Attendance","Courses","Homework","Assignments","Exams","Results","Transport","Library","Events","Grievance"].includes(active)) {
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
    content = <RoleModule title={active} user={user} />;
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
