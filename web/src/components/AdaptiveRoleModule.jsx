import React from "react";
import RoleModule from "./RoleModule";
import { displayMenuLabel } from "../institutionUI";

const CONFIG = {
  Teacher: {
    School: { hero:"Teacher Classroom", note:"Manage classes, homework, attendance, results and parent communication.", chips:["Classes","Homework","Report Cards"] },
    College: { hero:"Faculty Academic Workspace", note:"Manage courses, semester assessments, advisees and academic delivery.", chips:["Courses","Assessments","Advisees"] },
    University: { hero:"Faculty & Research Workspace", note:"Teaching, supervision, research and university academic activity.", chips:["Courses","Research","Supervision"] }
  },
  "Parent / Guardian": {
    School:{ hero:"Parent & Child", note:"Follow your child's learning, school bus, fees, homework and safety.", chips:["Child","Bus & Safety","School Updates"] },
    College:{ hero:"Guardian Overview", note:"Authorized visibility into semester progress, finance and campus updates.", chips:["Progress","Finance","Updates"] },
    University:{ hero:"Sponsor / Guardian Access", note:"Authorized academic, student-finance and support information.", chips:["Academic","Finance","Support"] }
  },
  "Institution Admin": {
    School:{ hero:"School Administration", note:"Operate classes, admissions, teachers, fees, buses and school services.", chips:["Academic","Operations","Parents"] },
    College:{ hero:"College Administration", note:"Operate departments, programs, semesters, faculty and campus services.", chips:["Departments","Programs","Campus"] },
    University:{ hero:"University Administration", note:"Govern schools, programs, research, finance and multi-campus services.", chips:["Governance","Academic","Research"] }
  },
  Accounts: {
    School:{ hero:"School Finance", note:"Fees, receipts, concessions, refunds and reconciliation.", chips:["Collections","Receipts","Reconciliation"] },
    College:{ hero:"College Finance", note:"Semester billing, scholarships, payments and finance reports.", chips:["Semester Billing","Scholarships","Reports"] },
    University:{ hero:"University Student Finance", note:"Student accounts, sponsors, aid, refunds and financial analytics.", chips:["Student Accounts","Aid","Analytics"] }
  },
  HR: {
    School:{ hero:"School HR", note:"Teacher and staff lifecycle, attendance, leave and recruitment.", chips:["Teachers","Staff","Leave"] },
    College:{ hero:"College HR", note:"Faculty and staff records, recruitment, leave and performance.", chips:["Faculty","Recruitment","Performance"] },
    University:{ hero:"University People Operations", note:"Faculty appointments, workforce lifecycle, performance and analytics.", chips:["Appointments","Workforce","Analytics"] }
  },
  "Campus Admin": {
    School:{ hero:"School Operations", note:"School attendance, buses, visitors, inventory, assets and safety.", chips:["School Day","Transport","Safety"] },
    College:{ hero:"Campus Operations", note:"Campus services, transport, visitors, facilities and safety.", chips:["Services","Facilities","Safety"] },
    University:{ hero:"University Campus Operations", note:"Campus presence, facilities, transport, services and incident oversight.", chips:["Campus Services","Facilities","Incidents"] }
  },
  Auditor: {
    School:{ hero:"School Audit & Compliance", note:"Read-only review of evidence, exceptions and operational controls.", chips:["Audit","Evidence","Exceptions"] },
    College:{ hero:"College Audit & Compliance", note:"Read-only academic, finance and campus control review.", chips:["Controls","Evidence","Reports"] },
    University:{ hero:"Governance, Risk & Audit", note:"Read-only institutional controls, evidence, risk and compliance review.", chips:["Governance","Risk","Audit"] }
  }
};

export default function AdaptiveRoleModule({title,user,ui}){
  const cfg=CONFIG[user.role]?.[ui.label];
  if(!cfg) return <RoleModule title={title} user={user}/>;
  return <div className={"adaptive-role-module arm-"+ui.label.toLowerCase()}>
    <section className="module-context">
      <div>
        <span className="eyebrow">{ui.label} • {user.role}</span>
        <h1>{displayMenuLabel(title,ui)}</h1>
        <p>{cfg.note}</p>
      </div>
      <div className="context-chips">{cfg.chips.map(x=><span key={x}>{x}</span>)}</div>
    </section>
    <RoleModule title={title} user={user}/>
  </div>
}
