import React, { useEffect, useState } from "react";
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
    columns: ["Event", "Type", "Date", "Time", "Venue", "Organizer", "Registration", "Status", "Action"],
    empty: "No events are currently available for your student account.",
  },
  Grievance: {
    title: "Grievance",
    subtitle: "Raise and track your student support requests.",
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
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/v1/student/profile")
      .then((response) => { setProfile(response.data); setError(""); })
      .catch((e) => setError(e?.response?.data?.detail || "Unable to load student profile."));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!profile) return <section className="panel">Loading student profile...</section>;

  const rows = [
    ["Name", profile.name || user?.name || "—"],
    ["Email", profile.email || user?.email || "—"],
    ["Status", profile.status || "—"],
    ["Campus", profile.campus_name || (profile.campus_id ? "Campus "+profile.campus_id : "—")],
    ["Institution", ui?.institutionName || "—"],
    ["Institution Type", ui?.label || "—"],
  ];

  return <>
    <section className="panel structure-table">
      <div className="panel-title"><b>Student Identity</b><span>Live</span></div>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Field</th><th>Value</th></tr></thead>
          <tbody>{rows.map(([label, value]) => <tr key={label}><td><b>{label}</b></td><td>{value}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
    <section className="panel structure-table">
      <div className="panel-title"><b>Academic Assignments</b><span>{profile.academics?.length || 0}</span></div>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Type</th><th>Code</th><th>Academic Unit</th><th>Unit Type</th></tr></thead>
          <tbody>{profile.academics?.length ? profile.academics.map((row) => <tr key={row.assignment_type + "-" + row.unit_id}><td>{row.assignment_type.replaceAll("_", " ")}</td><td>{row.unit_code || "—"}</td><td><b>{row.unit_name}</b></td><td>{row.unit_type.replaceAll("_", " ")}</td></tr>) : <tr><td colSpan="4" className="empty-cell">No active academic assignments are available.</td></tr>}</tbody>
        </table>
      </div>
    </section>
    <section className="panel structure-table">
      <div className="panel-title"><b>Guardians</b><span>{profile.guardians?.length || 0}</span></div>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Name</th><th>Relationship</th></tr></thead>
          <tbody>{profile.guardians?.length ? profile.guardians.map((row, index) => <tr key={index}><td><b>{row.name}</b></td><td>{row.relationship}</td></tr>) : <tr><td colSpan="2" className="empty-cell">No guardian is linked to this student account.</td></tr>}</tbody>
        </table>
      </div>
    </section>
  </>;
}

function StudentTransport() {
  const [transport, setTransport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/v1/student/transport")
      .then((response) => { setTransport(response.data); setError(""); })
      .catch((e) => setError(e?.response?.data?.detail || "Unable to load transport allocation."));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!transport) return <section className="panel">Loading transport allocation...</section>;
  if (!transport.allocated) return <EmptyTable columns={MODULES.Transport.columns} message={MODULES.Transport.empty} />;

  const vehicle = transport.vehicle
    ? [transport.vehicle.vehicle_number, transport.vehicle.label].filter(Boolean).join(" — ")
    : "—";
  return <section className="panel structure-table">
    <div className="panel-title"><b>Transport Allocation</b><span>Live</span></div>
    <div className="table-scroll">
      <table>
        <thead><tr>{MODULES.Transport.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody><tr>
          <td><b>{transport.route?.name || "—"}</b>{transport.route?.code ? " (" + transport.route.code + ")" : ""}</td>
          <td>{vehicle}</td>
          <td>{transport.stop?.name || "—"}</td>
          <td>{transport.pickup_time || "—"}</td>
          <td>{transport.drop_time || "—"}</td>
          <td>{transport.status || "—"}</td>
        </tr></tbody>
      </table>
    </div>
  </section>;
}


function StudentLibrary() {
  const [loans, setLoans] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/v1/student/library")
      .then((response) => { setLoans(response.data || []); setError(""); })
      .catch((e) => setError(e?.response?.data?.detail || "Unable to load library loans."));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!loans) return <section className="panel">Loading library loans...</section>;
  if (!loans.length) return <EmptyTable columns={MODULES.Library.columns} message={MODULES.Library.empty} />;

  const dateText = (value) => value ? new Date(value).toLocaleDateString() : "—";
  return <section className="panel structure-table">
    <div className="panel-title"><b>My Library Loans</b><span>{loans.length}</span></div>
    <div className="table-scroll">
      <table>
        <thead><tr>{MODULES.Library.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody>{loans.map((loan) => <tr key={loan.loan_id}>
          <td><b>{loan.book?.title || "—"}</b>{loan.book?.accession_no ? <div className="muted">{loan.book.accession_no}</div> : null}</td>
          <td>{loan.book?.author || "—"}</td>
          <td>{dateText(loan.issued_at)}</td>
          <td>{dateText(loan.due_at)}</td>
          <td>{dateText(loan.returned_at)}</td>
          <td>₹{Number(loan.fine_amount || 0).toFixed(2)}</td>
          <td>{loan.status || "—"}</td>
        </tr>)}</tbody>
      </table>
    </div>
  </section>;
}


function StudentEvents() {
  const [events, setEvents] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadEvents = () => api.get("/api/v1/student/events")
      .then((response) => { setEvents(response.data || []); setError(""); })
      .catch((e) => setError(e?.response?.data?.detail || "Unable to load events."));
  useEffect(() => {
    loadEvents();
  }, []);
  async function register(id){try{await api.post("/api/v1/student/events/"+id+"/register");setMessage("Event registration completed.");loadEvents()}catch(e){setError(e?.response?.data?.detail||"Unable to register for event.")}}

  if (error) return <div className="error">{error}</div>;
  if (!events) return <section className="panel">Loading events...</section>;
  if (!events.length) return <EmptyTable columns={MODULES.Events.columns} message={MODULES.Events.empty} />;

  return <>{message&&<div className="success">{message}</div>}<section className="panel structure-table">
    <div className="panel-title"><b>Student Events</b><span>{events.length}</span></div>
    <div className="table-scroll">
      <table>
        <thead><tr>{MODULES.Events.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody>{events.map((event) => {
          const starts = new Date(event.starts_at);
          return <tr key={event.id}>
            <td><b>{event.title}</b></td>
            <td>{event.event_type || "—"}</td>
            <td>{starts.toLocaleDateString()}</td>
            <td>{starts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td>
            <td>{event.venue || "—"}</td>
            <td>{event.organizer || "—"}</td>
            <td>{event.registration_status || "—"}</td>
            <td>{event.status || "—"}</td>
          <td>{event.registration_required && event.registration_status==="Not Registered" && (!event.registration_deadline || new Date(event.registration_deadline)>=new Date()) ? <button type="button" onClick={()=>register(event.id)}>Register</button> : event.registration_required && event.registration_status==="Not Registered" ? "Closed" : "—"}</td></tr>;
        })}</tbody>
      </table>
    </div>
  </section></>;
}


export default function StudentAcademicModule({ title, ui, user }) {
  const config = MODULES[title];
  const [details, setDetails] = useState("");
  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState("General");
  const [priority, setPriority] = useState("Normal");
  const [grievances, setGrievances] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (title !== "Grievance") return;
    api.get("/api/v1/student/grievances")
      .then((response) => setGrievances(response.data || []))
      .catch((e) => setError(e?.response?.data?.detail || "Unable to load grievances."));
  }, [title]);

  if (!config) return null;

  async function raiseSupport() {
    const value = details.trim();
    if (!subject.trim() || !value) {
      setError("Please enter the grievance subject and details.");
      setMessage("");
      return;
    }
    try {
      setSaving(true);
      setError("");
      setMessage("");
      const response = await api.post("/api/v1/student/grievances", {
        subject: subject.trim(), details: value, category, priority,
      });
      setSubject("");
      setDetails("");
      setCategory("General");
      setPriority("Normal");
      setGrievances((rows) => [response.data, ...rows]);
      setMessage("Grievance " + response.data.ticket_no + " submitted.");
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

    {title === "My Profile" ? <StudentProfile user={user} ui={ui} /> : title === "Transport" ? <StudentTransport /> : title === "Library" ? <StudentLibrary /> : title === "Events" ? <StudentEvents /> : <>
      {title === "Grievance" && <section className="panel">
        <div className="panel-title"><b>Raise Grievance</b><span>Student Support</span></div>
        <label>Subject</label>
        <input value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="Short grievance subject" />
        <label>Category</label>
        <input value={category} onChange={(event) => setCategory(event.target.value)} placeholder="Academic, Transport, Library..." />
        <label>Priority</label>
        <select value={priority} onChange={(event) => setPriority(event.target.value)}>
          <option>Low</option><option>Normal</option><option>High</option><option>Urgent</option>
        </select>
        <label>Details</label>
        <textarea value={details} onChange={(event) => setDetails(event.target.value)} placeholder="Describe the issue or support you need" />
        <div className="actions">
          <button className="primary" type="button" disabled={saving || !subject.trim() || !details.trim()} onClick={raiseSupport}>
            {saving ? "Submitting..." : "Submit Grievance"}
          </button>
        </div>
      </section>}
      {title === "Grievance" ? (grievances.length ? <section className="panel structure-table"><div className="panel-title"><b>My Grievances</b><span>{grievances.length}</span></div><div className="table-scroll"><table><thead><tr>{config.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{grievances.map((row) => <tr key={row.id}><td><b>{row.ticket_no}</b></td><td>{row.category}</td><td>{new Date(row.created_at).toLocaleString()}</td><td>{row.priority}</td><td>{row.status}</td><td>{row.latest_update || "Awaiting response"}</td></tr>)}</tbody></table></div></section> : <EmptyTable columns={config.columns} message={config.empty} />) : <EmptyTable columns={config.columns} message={config.empty} />}
    </>}
  </div>;
}
