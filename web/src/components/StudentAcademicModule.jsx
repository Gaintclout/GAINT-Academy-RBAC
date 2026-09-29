import React, { useState } from "react";
import { api } from "../api";

const MODULES = {
  "My Profile": {
    title: "My Profile",
    subtitle: "Your authenticated GAINT Academy identity.",
    columns: ["Field", "Value"],
  },
  Transport: {
    title: "Transport",
    subtitle: "Your route, vehicle, stop, pickup and drop information.",
    columns: ["Route", "Vehicle", "Stop", "Pickup", "Drop", "Status"],
    empty: "No transport allocation is available for your student account.",
  },
  Library: {
    title: "Library",
    subtitle: "Your borrowed books, due dates, returns and fines.",
    columns: ["Book", "Author", "Issue Date", "Due Date", "Return Date", "Fine", "Status"],
    empty: "No library loans are available for your student account.",
  },
  Events: {
    title: "Events",
    subtitle: "Events available to your student account.",
    columns: ["Event", "Date", "Time", "Location", "Registration", "Status"],
    empty: "No events are currently available for your student account.",
  },
  Grievance: {
    title: "Grievance",
    subtitle: "Raise a student support request. Ticket history will appear when the grievance API is available.",
    columns: ["Ticket", "Category", "Created", "Priority", "Status", "Latest Update"],
    empty: "No grievance history is available.",
  },
};

function EmptyTable({ columns, message }) {
  return <section className="panel structure-table">
    <div className="table-scroll">
      <table>
        <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody><tr><td colSpan={columns.length} className="empty-cell">{message}</td></tr></tbody>
      </table>
    </div>
  </section>;
}

function StudentProfile({ user, ui }) {
  const rows = [
    ["Name", user?.name || "—"],
    ["Email", user?.email || "—"],
    ["Role", user?.role || "Student"],
    ["Institution", ui?.institutionName || "—"],
    ["Institution Type", ui?.label || "—"],
  ];
  return <section className="panel structure-table">
    <div className="table-scroll">
      <table>
        <thead><tr><th>Field</th><th>Value</th></tr></thead>
        <tbody>{rows.map(([label, value]) => <tr key={label}><td><b>{label}</b></td><td>{value}</td></tr>)}</tbody>
      </table>
    </div>
    <div className="readonly-note">Academic profile fields such as admission number, program, section and guardian will appear only after they are supplied by the student profile API.</div>
  </section>;
}

export default function StudentAcademicModule({ title, ui, user }) {
  const config = MODULES[title];
  const [details, setDetails] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  if (!config) return null;

  async function raiseSupport() {
    const value = details.trim();
    if (!value) {
      setError("Please enter the grievance details.");
      setMessage("");
      return;
    }
    try {
      setSaving(true);
      setError("");
      setMessage("");
      const response = await api.post("/api/v1/module-actions/create_grievance", {
        page: "Grievance",
        details: value,
      });
      setDetails("");
      setMessage(response.data?.message || "Grievance request submitted.");
    } catch (e) {
      setError(e?.response?.data?.detail || "Unable to submit grievance.");
    } finally {
      setSaving(false);
    }
  }

  return <div className={"student-module student-module-" + ui.label.toLowerCase()}>
    <div className="page-title">
      <div>
        <span className="eyebrow">{ui.label} Student</span>
        <h1>{config.title}</h1>
        <p>{config.subtitle}</p>
      </div>
    </div>

    {error && <div className="error">{error}</div>}
    {message && <div className="success">{message}</div>}

    {title === "My Profile" ? <StudentProfile user={user} ui={ui} /> : <>
      {title === "Grievance" && <section className="panel">
        <div className="panel-title"><b>Raise Grievance</b><span>Student Support</span></div>
        <label>Details</label>
        <textarea
          value={details}
          onChange={(event) => setDetails(event.target.value)}
          placeholder="Describe the issue or support you need"
        />
        <div className="actions">
          <button className="primary" type="button" disabled={saving || !details.trim()} onClick={raiseSupport}>
            {saving ? "Submitting..." : "Submit Grievance"}
          </button>
        </div>
      </section>}
      <EmptyTable columns={config.columns} message={config.empty} />
    </>}
  </div>;
}
