import React from "react";
import { api } from "../api";

const DATA = {
  School: {
    title: "My Fees",
    subtitle: "Academic Year 2026-27",
    totals: [["Total Fees","₹42,000"],["Paid Amount","₹32,000"],["Balance Due","₹10,000"]],
    rows: [
      ["Term I Tuition Fee","₹25,000","Tuition","Paid"],
      ["Transport Fee","₹6,000","Transport","Paid"],
      ["Activity Fee","₹1,000","Activities","Paid"],
      ["Term II Tuition Fee","₹10,000","Tuition","Due"]
    ]
  },
  College: {
    title: "Semester Fees",
    subtitle: "Semester IV • 2026-27",
    totals: [["Semester Fee","₹58,500"],["Paid Amount","₹45,000"],["Outstanding","₹13,500"]],
    rows: [
      ["Semester Tuition Fee","₹35,000","Tuition","Paid"],
      ["Laboratory Fee","₹5,000","Academic","Paid"],
      ["Examination Fee","₹3,500","Examination","Due"],
      ["Library Fee","₹2,000","Library","Paid"],
      ["Hostel Fee","₹10,000","Hostel","Due"],
      ["Student Activities","₹3,000","Campus","Paid"]
    ]
  },
  University: {
    title: "Student Finance",
    subtitle: "School of Engineering • Semester VI",
    totals: [["Total Charges","₹1,25,000"],["Paid Amount","₹95,000"],["Outstanding","₹30,000"],["Financial Aid","₹20,000"]],
    rows: [
      ["Academic Tuition","₹70,000","SEM-VI","Paid"],
      ["Laboratory Charges","₹10,000","CSE-LAB","Paid"],
      ["Examination Fee","₹5,000","EXAM-26","Paid"],
      ["Hostel Fee","₹25,000","HOSTEL-H4","Due"],
      ["Research Lab Fee","₹5,000","RLAB-CSE","Paid"],
      ["University Services","₹10,000","UNI-SVC","Due"]
    ]
  }
};

export default function StudentFinance({ ui }) {
  const data = DATA[ui.label] || DATA.University;
  async function payment() {
    await api.post("/api/v1/module-actions/pay", { page: "Fees", details: "Payment requested from adaptive student finance UI." });
    window.alert("Payment action submitted.");
  }
  return (
    <div className={"finance-page finance-" + ui.label.toLowerCase()}>
      <div className="page-title">
        <div><h1>{data.title}</h1><p>{data.subtitle}</p></div>
        <div className="page-actions">
          <button className="secondary" type="button">Download Statement</button>
          <button className="primary" type="button" onClick={payment}>Make Payment</button>
        </div>
      </div>

      <div className="finance-kpis">
        {data.totals.map(([label,value]) => <article key={label}><small>{label}</small><strong>{value}</strong></article>)}
      </div>

      <section className="panel finance-panel">
        <div className="panel-title"><b>{ui.label === "University" ? "Account Summary" : "Fee Breakdown"}</b><span>Current period</span></div>
        <div className="table-scroll">
          <table>
            <thead><tr><th>Description</th><th>Amount</th><th>Reference / Category</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              {data.rows.map(row => (
                <tr key={row[0]}>
                  <td><b>{row[0]}</b></td><td>{row[1]}</td><td>{row[2]}</td>
                  <td><span className={"fee-status " + row[3].toLowerCase()}>{row[3]}</span></td>
                  <td><button className="table-action" type="button">{row[3] === "Due" ? "Pay Now" : "View Receipt"}</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
