import React from "react";

const ROLE_COPY = {
  "Institution Admin": {
    School:["School Administration","Manage students, teachers, classes, fees and school operations."],
    College:["College Administration","Manage departments, programs, semesters, faculty and campus operations."],
    University:["University Administration","Manage schools, faculties, programs, research and university operations."]
  },
  Teacher:{
    School:["Teacher Workspace","Classes, homework, attendance and student progress."],
    College:["Faculty Workspace","Courses, assignments, attendance and semester assessments."],
    University:["Faculty & Research Workspace","Teaching, assessments, advisees and research activities."]
  },
  "Parent / Guardian":{
    School:["Parent Dashboard","Your child's school day, homework, fees, bus and safety."],
    College:["Guardian Overview","Academic progress, fees and important student updates."],
    University:["Sponsor / Guardian Overview","Authorized academic, finance and student support information."]
  },
  Accounts:{
    School:["School Finance","Fee collection, receipts, concessions and reconciliation."],
    College:["College Finance","Semester fees, scholarships, refunds and reconciliation."],
    University:["University Finance","Student accounts, program charges, aid, sponsors and financial reporting."]
  },
  HR:{
    School:["School HR","Teachers, non-teaching staff, leave and recruitment."],
    College:["College HR","Faculty, staff, departments, leave and recruitment."],
    University:["University HR","Faculty and staff lifecycle, appointments, performance and workforce reporting."]
  },
  "Campus Admin":{
    School:["School Operations","Campus attendance, buses, visitors, assets and student safety."],
    College:["Campus Operations","Facilities, transport, visitors, inventory and campus safety."],
    University:["University Campus Operations","Multi-facility operations, services, assets and campus safety."]
  },
  Auditor:{
    School:["Audit & Compliance","Review school controls, evidence, exceptions and audit activity."],
    College:["Audit & Compliance","Review academic, finance and campus controls with read-only access."],
    University:["Governance, Audit & Compliance","Review institutional controls, evidence, exceptions and audit trails."]
  }
};

const ROLE_CARDS = {
  "Institution Admin":{
    School:[["Students","1,240"],["Teachers","86"],["Attendance Today","94%"],["Pending Actions","18"]],
    College:[["Students","3,860"],["Faculty","214"],["Programs","18"],["Pending Actions","24"]],
    University:[["Students","12,480"],["Faculty","742"],["Programs","64"],["Research Projects","128"]]
  },
  Teacher:{
    School:[["Classes Today","5"],["My Students","148"],["Homework to Review","22"],["Attendance Pending","2"]],
    College:[["Courses","4"],["Students","186"],["Assignments to Grade","37"],["Advisees","18"]],
    University:[["Courses","3"],["Advisees","12"],["Assessments","28"],["Research Projects","2"]]
  },
  "Parent / Guardian":{
    School:[["Attendance","91%"],["Homework","3 Pending"],["Bus ETA","12 min"],["Fee Due","₹0"]],
    College:[["Attendance","87%"],["Semester","IV"],["Fee Due","₹13,500"],["Updates","3"]],
    University:[["Academic Standing","Good"],["CGPA","8.6"],["Finance Due","₹30,000"],["Updates","2"]]
  },
  Accounts:{
    School:[["Today's Collection","₹2.45L"],["Pending Fees","₹6.2L"],["Receipts","163"],["Refunds","4"]],
    College:[["Semester Collection","₹42.8L"],["Outstanding","₹11.4L"],["Scholarships","86"],["Refunds","12"]],
    University:[["Student Receivables","₹1.84Cr"],["Collected","₹6.42Cr"],["Aid / Sponsors","₹82L"],["Reconciliation","96%"]]
  },
  HR:{
    School:[["Teachers","86"],["Staff","100"],["Present Today","174"],["Leave Requests","8"]],
    College:[["Faculty","214"],["Staff","168"],["Open Positions","12"],["Leave Requests","18"]],
    University:[["Faculty","742"],["Staff","1,086"],["Open Positions","34"],["Reviews Due","46"]]
  },
  "Campus Admin":{
    School:[["Students On Campus","1,102"],["Buses Active","18"],["Visitors","14"],["Safety Alerts","2"]],
    College:[["Campus Footfall","3,420"],["Shuttles","12"],["Visitors","38"],["Service Requests","16"]],
    University:[["Campus Population","9,840"],["Shuttles","28"],["Facilities","64"],["Open Incidents","7"]]
  },
  Auditor:{
    School:[["Audit Events","86"],["Exceptions","4"],["Evidence Items","42"],["Reviews","6"]],
    College:[["Audit Events","164"],["Exceptions","8"],["Controls","72"],["Reviews","11"]],
    University:[["Audit Events","486"],["Exceptions","14"],["Controls","128"],["Reviews","24"]]
  }
};

export default function InstitutionRoleDashboard({user,ui}){
  const copy=ROLE_COPY[user.role]?.[ui.label] || [user.role+" Dashboard",ui.label+" workspace"];
  const cards=ROLE_CARDS[user.role]?.[ui.label] || [];
  return <div className={"role-dashboard role-"+ui.label.toLowerCase()}>
    <section className="role-hero">
      <div><span className="eyebrow">{ui.label} • {user.role}</span><h1>{copy[0]}</h1><p>{copy[1]}</p></div>
      <div className="hero-badge">{ui.label}</div>
    </section>
    <div className="module-kpis">{cards.map(([l,v])=><article key={l}><small>{l}</small><strong>{v}</strong></article>)}</div>
    <div className="student-grid">
      <section className="panel"><div className="panel-title"><b>{ui.label} Operational Overview</b><span>Today</span></div>
        <div className="activity">
          {["Priority items reviewed","Role-scoped activity synchronized","New records available","Reports ready for review"].map((x,i)=><div key={x}><span className="dot">{i+1}</span><div><b>{x}</b><small>{(i+1)*9} min ago</small></div></div>)}
        </div>
      </section>
      <section className="panel"><div className="panel-title"><b>Workspace Focus</b></div>
        <div className="quick-tile-grid">
          {(ui.label==="School"?["Daily Operations","Student Support","Communication","Reports"]:ui.label==="College"?["Semester Operations","Departments","Campus Services","Reports"]:["Academic Governance","Research","Campus Services","Analytics"]).map(x=><button type="button" key={x}>{x}<span>›</span></button>)}
        </div>
      </section>
    </div>
  </div>
}
