import React from "react";

export default function StudentDashboard({ user, ui }) {
  const firstName = user?.name?.split(/\s+/)[0] || "Student";
  const items =
    ui.label === "School"
      ? [
          ["09:00", "Mathematics", "Room 101"],
          ["10:00", "Science", "Room 101"],
          ["11:00", "English", "Room 102"],
          ["12:00", "Social Studies", "Room 103"]
        ]
      : ui.label === "College"
        ? [
            ["Sep 28", "Data Structures Assignment", "Pending"],
            ["Oct 02", "DBMS Internal Exam", "Upcoming"],
            ["Oct 05", "Project Review", "Scheduled"],
            ["Oct 08", "Technical Seminar", "Open"]
          ]
        : [
            ["Oct 10", "End Semester Examination", "Academic"],
            ["Oct 18", "Project Viva", "Assessment"],
            ["Oct 25", "Research Seminar", "Research"],
            ["Oct 30", "Elective Registration", "Registration"]
          ];

  return (
    <div className={"institution-dashboard institution-" + ui.label.toLowerCase()}>
      <section className="student-hero">
        <div>
          <span className="eyebrow">{ui.label} Student</span>
          <h1>{ui.dashboard.greeting}, {firstName}! 👋</h1>
          <p>{ui.dashboard.subtitle}</p>
        </div>
        <div className="hero-badge">{ui.label}</div>
      </section>

      <div className="student-kpis">
        {ui.dashboard.cards.map(([label, value, hint]) => (
          <article className="student-kpi" key={label}>
            <small>{label}</small>
            <strong>{value}</strong>
            <span>{hint}</span>
          </article>
        ))}
      </div>

      <div className="student-grid">
        <section className="panel">
          <div className="panel-title">
            <b>{ui.label === "School" ? "Today's Timetable" : ui.label === "College" ? "Upcoming Deadlines" : "Upcoming Academic Events"}</b>
            <span>View all</span>
          </div>
          <div className="timeline-list">
            {items.map(([time, title, meta]) => (
              <div className="timeline-row" key={title}>
                <span>{time}</span>
                <b>{title}</b>
                <small>{meta}</small>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-title">
            <b>{ui.label === "School" ? "Quick Links" : ui.label === "College" ? "Career & Campus" : "Research & Campus"}</b>
          </div>
          <div className="quick-tile-grid">
            {(ui.label === "School"
              ? ["Homework", "My Bus", "Activities", "Library"]
              : ui.label === "College"
                ? ["Projects", "Internships", "Placements", "Clubs"]
                : ["Research", "Projects", "Publications", "Career"]
            ).map((item) => <button type="button" key={item}>{item}<span>›</span></button>)}
          </div>
        </section>
      </div>
    </div>
  );
}
